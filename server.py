#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
유튜브 텍스트 변환기 - 간결 버전
핵심 기능: 유튜브 영상 → 음성 추출 → 텍스트 변환
"""

import os
import uuid
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import yt_dlp
import whisper
import zipfile
import tempfile
import shutil

app = Flask(__name__)
CORS(app)

# 전역 변수
tasks = {}  # 작업 상태 저장
model = None  # Whisper 모델
temp_dir = tempfile.mkdtemp()  # 임시 디렉토리

# Whisper 모델 로드 (앱 시작 시)
def load_whisper_model():
    global model
    try:
        print("Whisper 모델 로딩 중...")
        model = whisper.load_model("base")  # base 모델 사용 (속도와 정확도 균형)
        print("Whisper 모델 로딩 완료")
    except Exception as e:
        print(f"Whisper 모델 로딩 실패: {e}")
        model = None

# 작업 상태 클래스
class ConversionTask:
    def __init__(self, task_id, url):
        self.task_id = task_id
        self.url = url
        self.progress = 0
        self.status = "준비 중..."
        self.completed = False
        self.success = False
        self.error = None
        self.files = []
        self.created_at = datetime.now()

# 메인 페이지
@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

# Favicon 처리 (404 에러 방지)
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content 응답으로 404 에러 방지

# 정적 파일 제공 (이미지, CSS 등)
@app.route('/<path:filename>')
def static_files(filename):
    # 보안을 위해 허용된 확장자만 제공
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.css', '.js', '.svg'}
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return "File type not allowed", 403
    
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        # MIME 타입 설정
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.ico': 'image/x-icon',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.svg': 'image/svg+xml'
        }
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return content, 200, {'Content-Type': mime_types.get(file_ext, 'application/octet-stream')}
    
    return "File not found", 404

# 헬스체크 엔드포인트
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'whisper_model': 'loaded' if model else 'not_loaded',
        'active_tasks': len([t for t in tasks.values() if not t.completed]),
        'total_tasks': len(tasks)
    })

# 통계 엔드포인트
@app.route('/stats')
def get_stats():
    completed_tasks = [t for t in tasks.values() if t.completed]
    successful_tasks = [t for t in completed_tasks if t.success]
    
    return jsonify({
        'total_tasks': len(tasks),
        'completed_tasks': len(completed_tasks),
        'successful_tasks': len(successful_tasks),
        'active_tasks': len([t for t in tasks.values() if not t.completed]),
        'success_rate': (len(successful_tasks) / max(len(completed_tasks), 1)) * 100,
        'model_status': 'loaded' if model else 'not_loaded'
    })

# 변환 요청 처리
@app.route('/convert', methods=['POST'])
def convert_video():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL이 필요합니다.'}), 400
        
        # 작업 ID 생성
        task_id = str(uuid.uuid4())
        task = ConversionTask(task_id, url)
        tasks[task_id] = task
        
        # 백그라운드에서 변환 시작
        thread = threading.Thread(target=process_video, args=(task,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'taskId': task_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 진행 상황 확인
@app.route('/progress/<task_id>')
def get_progress(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': '작업을 찾을 수 없습니다.'}), 404
    
    return jsonify({
        'progress': task.progress,
        'status': task.status,
        'completed': task.completed,
        'success': task.success,
        'error': task.error,
        'files': task.files
    })

# 파일 다운로드
@app.route('/download/<file_id>')
def download_file(file_id):
    # 모든 작업에서 파일 찾기
    for task in tasks.values():
        for file_info in task.files:
            if file_info['id'] == file_id:
                file_path = file_info['path']
                if os.path.exists(file_path):
                    return send_file(file_path, as_attachment=True, download_name=file_info['name'])
    
    return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

# 전체 파일 ZIP 다운로드
@app.route('/download-all/<task_id>')
def download_all(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': '작업을 찾을 수 없습니다.'}), 404
    
    # ZIP 파일 생성
    zip_path = os.path.join(temp_dir, f"{task_id}_all.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_info in task.files:
            if os.path.exists(file_info['path']):
                zipf.write(file_info['path'], file_info['name'])
    
    return send_file(zip_path, as_attachment=True, download_name=f"youtube_conversion_{task_id}.zip")

# 비디오 처리 함수
def process_video(task):
    try:
        # 1단계: 비디오 다운로드 및 음성 추출
        task.status = "영상 다운로드 중..."
        task.progress = 10
        
        file_paths = download_and_extract_audio(task)
        if not file_paths or not file_paths.get('audio'):
            raise Exception("파일 다운로드 실패")
        
        task.progress = 60
        task.status = "음성을 텍스트로 변환 중..."
        
        # 2단계: 음성을 텍스트로 변환
        text_path = convert_audio_to_text(task, file_paths['audio'])
        if not text_path:
            raise Exception("텍스트 변환 실패")
        
        task.progress = 90
        task.status = "파일 준비 중..."
        
        # 3단계: 결과 파일 정리
        prepare_result_files(task, file_paths['video'], file_paths['audio'], text_path)
        
        task.progress = 100
        task.status = "변환 완료!"
        task.completed = True
        task.success = True
        
    except Exception as e:
        task.error = str(e)
        task.completed = True
        task.success = False
        task.status = f"오류: {str(e)}"

# 비디오 다운로드 및 음성 추출 함수
def download_and_extract_audio(task):
    try:
        output_dir = os.path.join(temp_dir, task.task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # 1단계: MP4 비디오 다운로드
        video_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_dir, 'video_%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        video_path = None
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(task.url, download=True)
            title = info.get('title', 'unknown')
            
            # MP4 파일 찾기
            for file in os.listdir(output_dir):
                if file.startswith('video_') and (file.endswith('.mp4') or file.endswith('.webm')):
                    video_path = os.path.join(output_dir, file)
                    break
        
        task.progress = 30
        task.status = "음성 추출 중..."
        
        # 2단계: 음성 추출 (MP3)
        audio_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, 'audio_%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        audio_path = None
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.extract_info(task.url, download=True)
            
            # MP3 파일 찾기
            for file in os.listdir(output_dir):
                if file.startswith('audio_') and file.endswith('.mp3'):
                    audio_path = os.path.join(output_dir, file)
                    break
        
        return {'video': video_path, 'audio': audio_path}
        
    except Exception as e:
        print(f"다운로드 오류: {e}")
        return None

# 텍스트 변환 함수
def convert_audio_to_text(task, audio_path):
    try:
        if not model:
            raise Exception("Whisper 모델이 로드되지 않았습니다.")
        
        # Whisper로 음성 인식
        result = model.transcribe(audio_path, language='ko')
        text = result['text']
        
        # 텍스트 파일 저장
        output_dir = os.path.dirname(audio_path)
        text_path = os.path.join(output_dir, 'transcript.txt')
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return text_path
        
    except Exception as e:
        print(f"텍스트 변환 오류: {e}")
        return None

# 결과 파일 준비
def prepare_result_files(task, video_path, audio_path, text_path):
    task.files = []
    
    # 비디오 파일 추가
    if video_path and os.path.exists(video_path):
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(video_path)[1]
        task.files.append({
            'id': file_id,
            'name': f"video_{task.task_id}{ext}",
            'path': video_path,
            'type': 'video',
            'taskId': task.task_id
        })
    
    # 음성 파일 추가
    if audio_path and os.path.exists(audio_path):
        file_id = str(uuid.uuid4())
        task.files.append({
            'id': file_id,
            'name': f"audio_{task.task_id}.mp3",
            'path': audio_path,
            'type': 'audio',
            'taskId': task.task_id
        })
    
    # 텍스트 파일 추가
    if text_path and os.path.exists(text_path):
        file_id = str(uuid.uuid4())
        task.files.append({
            'id': file_id,
            'name': f"transcript_{task.task_id}.txt",
            'path': text_path,
            'type': 'text',
            'taskId': task.task_id
        })

# 임시 파일 정리 (24시간 후)
def cleanup_old_files():
    while True:
        try:
            current_time = datetime.now()
            expired_tasks = []
            
            for task_id, task in tasks.items():
                if current_time - task.created_at > timedelta(hours=24):
                    expired_tasks.append(task_id)
                    
                    # 파일 삭제
                    task_dir = os.path.join(temp_dir, task_id)
                    if os.path.exists(task_dir):
                        shutil.rmtree(task_dir)
            
            # 만료된 작업 제거
            for task_id in expired_tasks:
                del tasks[task_id]
            
            time.sleep(3600)  # 1시간마다 확인
            
        except Exception as e:
            print(f"파일 정리 오류: {e}")
            time.sleep(3600)

if __name__ == '__main__':
    # Whisper 모델 로드
    load_whisper_model()
    
    # 파일 정리 스레드 시작
    cleanup_thread = threading.Thread(target=cleanup_old_files)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    print("유튜브 텍스트 변환기 서버 시작")
    print("브라우저에서 http://localhost:5000 접속")
    
    app.run(host='0.0.0.0', port=5000, debug=False)