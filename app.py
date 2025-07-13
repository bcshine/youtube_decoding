#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
유튜브 텍스트 변환기 - Streamlit 버전
핵심 기능: 유튜브 영상 → 음성 추출 → 텍스트 변환
"""

import streamlit as st
import os
import uuid
import tempfile
import zipfile
import io
from datetime import datetime
import yt_dlp
import whisper
import re
from PIL import Image

# 기본 페이지 설정
st.set_page_config(
    page_title="YouTube 컨텐츠 변환기",
    page_icon="🎬",
    layout="centered"
)

# 세션 상태 초기화
if 'model' not in st.session_state:
    st.session_state.model = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
if 'conversion_complete' not in st.session_state:
    st.session_state.conversion_complete = False
if 'result_files' not in st.session_state:
    st.session_state.result_files = []

# 페이지 로드 시 이전 결과 정리
if st.session_state.conversion_complete and st.session_state.result_files:
    # 파일이 실제로 존재하지 않으면 세션 초기화
    if not any(os.path.exists(f['path']) for f in st.session_state.result_files):
        st.session_state.conversion_complete = False
        st.session_state.result_files = []

@st.cache_resource
def load_whisper_model():
    """Whisper 모델 로드 (캐시됨)"""
    try:
        model = whisper.load_model("base")
        return model
    except Exception as e:
        st.error(f"Whisper 모델 로딩 실패: {e}")
        return None

def is_valid_youtube_url(url):
    """유튜브 URL 유효성 검사"""
    youtube_regex = r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+'
    return re.match(youtube_regex, url) is not None

def download_and_extract_audio(url, output_dir, progress_callback=None):
    """유튜브 비디오 다운로드 및 음성 추출"""
    try:
        if progress_callback:
            progress_callback("영상 정보 가져오는 중...", 10)
        
        # 1단계: MP4 비디오 다운로드
        video_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_dir, 'video_%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        video_path = None
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'unknown')
            
            # MP4 파일 찾기
            for file in os.listdir(output_dir):
                if file.startswith('video_') and (file.endswith('.mp4') or file.endswith('.webm')):
                    video_path = os.path.join(output_dir, file)
                    break
        
        if not video_path:
            raise Exception("비디오 다운로드 실패")
        
        if progress_callback:
            progress_callback("음성 추출 중...", 40)
        
        # 2단계: 음성 추출 (MP3로 변경)
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
            ydl.extract_info(url, download=True)
            
            # MP3 파일 찾기
            for file in os.listdir(output_dir):
                if file.startswith('audio_') and file.endswith('.mp3'):
                    audio_path = os.path.join(output_dir, file)
                    break
        
        if not audio_path:
            raise Exception("음성 추출 실패")
        
        return {
            'video': video_path,
            'audio': audio_path,
            'title': title
        }
        
    except Exception as e:
        raise Exception(f"다운로드 실패: {str(e)}")

def convert_audio_to_text(audio_path, model, progress_callback=None):
    """음성을 텍스트로 변환"""
    try:
        if progress_callback:
            progress_callback("음성을 텍스트로 변환 중...", 70)
        
        result = model.transcribe(audio_path, language='ko')
        text = result['text']
        
        # 텍스트 파일 저장
        text_path = audio_path.replace('.mp3', '_transcript.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return text_path, text
        
    except Exception as e:
        raise Exception(f"텍스트 변환 실패: {str(e)}")

def main():
    # 간단한 헤더
    st.markdown("<h1 style='font-size: 32px'>* YouTube 컨텐츠 변환기 *</h1>", unsafe_allow_html=True)
    st.write("YouTube 영상을 텍스트로 변환하는 도구입니다.")
    
    # Whisper 모델 로드
    if st.session_state.model is None:
        with st.spinner('Whisper 모델을 로딩 중입니다...'):
            st.session_state.model = load_whisper_model()
    
    if st.session_state.model:
        st.success("✅ AI 모델이 준비되었습니다!")
    else:
        st.error("❌ 모델 로드에 실패했습니다. 페이지를 새로고침해주세요.")
        return
    
    # URL 입력
    st.subheader("🔗 YouTube URL 입력")
    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="youtube_url"
    )
    
    # 변환 버튼
    convert_button = st.button(
        "🚀 변환 시작",
        type="primary"
    )
    
    if convert_button:
        if not url:
            st.error("❌ YouTube URL을 입력해주세요.")
        elif not is_valid_youtube_url(url):
            st.error("❌ 올바른 YouTube URL을 입력해주세요.")
        else:
            # 변환 프로세스 시작
            convert_video(url)
    

    
    # 결과 표시 - 조건을 더 엄격하게 확인
    if (st.session_state.conversion_complete and 
        st.session_state.result_files and 
        any(os.path.exists(f['path']) for f in st.session_state.result_files)):
        display_results()

def convert_video(url):
    """비디오 변환 프로세스"""
    try:
        st.info("🔄 변환을 시작합니다...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(message, progress):
            progress_bar.progress(progress / 100)
            status_text.info(message)
        
        # 임시 디렉토리 생성
        task_id = str(uuid.uuid4())
        output_dir = os.path.join(st.session_state.temp_dir, task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # 1단계: 다운로드 및 음성 추출
        update_progress("📥 영상 다운로드 및 음성 추출 중...", 20)
        file_paths = download_and_extract_audio(url, output_dir, update_progress)
        
        # 2단계: 텍스트 변환
        update_progress("🤖 AI가 음성을 텍스트로 변환 중...", 60)
        text_path, transcript_text = convert_audio_to_text(
            file_paths['audio'], 
            st.session_state.model, 
            update_progress
        )
        
        # 3단계: 결과 파일 준비
        update_progress("📋 결과 파일 준비 중...", 90)
        
        # 결과 파일 정보 저장 (비디오, 오디오, 텍스트 모두 포함)
        st.session_state.result_files = []
        
        # 비디오 파일 추가
        if file_paths['video'] and os.path.exists(file_paths['video']):
            video_ext = os.path.splitext(file_paths['video'])[1]
            st.session_state.result_files.append({
                'name': f"{file_paths['title']}_video{video_ext}",
                'path': file_paths['video'],
                'type': 'video'
            })
        
        # 오디오 파일 추가
        if file_paths['audio'] and os.path.exists(file_paths['audio']):
            st.session_state.result_files.append({
                'name': f"{file_paths['title']}_audio.mp3",
                'path': file_paths['audio'],
                'type': 'audio'
            })
        
        # 텍스트 파일 추가
        if text_path and os.path.exists(text_path):
            st.session_state.result_files.append({
                'name': f"{file_paths['title']}_transcript.txt",
                'path': text_path,
                'type': 'text',
                'content': transcript_text
            })
        
        update_progress("✨ 변환 완료!", 100)
        st.session_state.conversion_complete = True
        
        # 성공 메시지
        st.success("🎉 변환이 완료되었습니다!")
        
        # 페이지 새로고침으로 결과 표시
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 변환 중 오류가 발생했습니다: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def display_results():
    """결과 표시 - 기본 스타일"""
    if not st.session_state.result_files:
        return
    
    # 실제 존재하는 파일만 필터링
    valid_files = [f for f in st.session_state.result_files if os.path.exists(f['path'])]
    if not valid_files:
        return
    
    st.success("✅ 변환이 완료되었습니다!")
    
    # 텍스트 내용 표시 (있는 경우)
    text_file = next((f for f in valid_files if f['type'] == 'text'), None)
    if text_file and 'content' in text_file:
        st.subheader("📝 변환된 텍스트")
        st.text_area(
            "변환 결과",
            value=text_file['content'],
            height=200,
            key="transcript_display"
        )
    
    # 다운로드 섹션
    st.subheader("💾 파일 다운로드")
    
    # 개별 파일 다운로드
    for file_info in valid_files:
        with open(file_info['path'], 'rb') as f:
            file_data = f.read()
        
        # 파일 타입에 따른 라벨
        type_labels = {
            'video': '🎬 비디오 파일',
            'audio': '🎵 오디오 파일', 
            'text': '📄 텍스트 파일'
        }
        
        label = type_labels.get(file_info['type'], '📁 파일')
        
        st.download_button(
            label=f"{label}: {file_info['name']}",
            data=file_data,
            file_name=file_info['name'],
            key=f"download_{file_info['name']}"
        )
    
    # ZIP 파일 다운로드
    if len(valid_files) > 1:
        st.subheader("📦 전체 다운로드")
        
        # ZIP 파일 생성
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_info in valid_files:
                zip_file.write(file_info['path'], file_info['name'])
        
        zip_data = zip_buffer.getvalue()
        
        st.download_button(
            label="📦 모든 파일을 ZIP으로 다운로드",
            data=zip_data,
            file_name="youtube_conversion_files.zip",
            mime="application/zip"
        )
    
    # 새 변환 버튼
    if st.button("🔄 새로운 변환 시작"):
        # 세션 상태 초기화
        st.session_state.conversion_complete = False
        st.session_state.result_files = []
        st.rerun()

def create_zip_file():
    """결과 파일들을 ZIP으로 압축"""
    try:
        import io
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_info in st.session_state.result_files:
                if os.path.exists(file_info['path']):
                    zip_file.write(file_info['path'], file_info['name'])
        
        return zip_buffer.getvalue()
    except Exception as e:
        st.error(f"ZIP 파일 생성 실패: {str(e)}")
        return None

if __name__ == "__main__":
    main()