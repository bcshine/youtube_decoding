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
from datetime import datetime
import yt_dlp
import whisper
import re
from PIL import Image

# 페이지 설정
# 로고 이미지를 PIL Image로 로드
try:
    logo_image = Image.open("logo2.png")
except:
    logo_image = "🎬"  # 로고 파일이 없으면 이모지 사용

st.set_page_config(
    page_title="유튜브 텍스트 변환기",
    page_icon=logo_image,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 스타일링
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-size: 16px;
        font-weight: 500;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'model' not in st.session_state:
    st.session_state.model = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
if 'conversion_complete' not in st.session_state:
    st.session_state.conversion_complete = False
if 'result_files' not in st.session_state:
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
    # 헤더 - 로고를 가로 중앙에 배치
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 로고 파일이 존재하는지 확인
        logo_path = "logo2.png"
        if os.path.exists(logo_path):
            # 중앙 정렬을 위한 컨테이너
            st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
            st.image(logo_path, width=100)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # 로고가 없으면 이모지로 대체
            st.markdown("<div style='text-align: center; font-size: 60px;'>🎬</div>", unsafe_allow_html=True)
    
    st.title("유튜브 텍스트 변환기")
    
    st.markdown("---")
    
    # Whisper 모델 로드
    if st.session_state.model is None:
        with st.spinner("Whisper 모델 로딩 중..."):
            st.session_state.model = load_whisper_model()
    
    if st.session_state.model is None:
        st.error("❌ Whisper 모델을 로드할 수 없습니다. 페이지를 새로고침해주세요.")
        return
    
    st.success("✅ Whisper 모델 로드 완료")
    
    # URL 입력
    st.subheader("📝 유튜브 URL 입력")
    url = st.text_input(
        "유튜브 URL을 입력하세요:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="유튜브 동영상의 전체 URL을 입력해주세요."
    )
    
    # 변환 버튼
    if st.button("🚀 변환 시작", type="primary"):
        if not url:
            st.error("❌ 유튜브 URL을 입력해주세요.")
        elif not is_valid_youtube_url(url):
            st.error("❌ 올바른 유튜브 URL을 입력해주세요.")
        else:
            # 변환 프로세스 시작
            convert_video(url)
    
    # 결과 표시
    if st.session_state.conversion_complete and st.session_state.result_files:
        display_results()

def convert_video(url):
    """비디오 변환 프로세스"""
    try:
        # 진행률 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(message, progress):
            progress_bar.progress(progress / 100)
            status_text.text(message)
        
        # 임시 디렉토리 생성
        task_id = str(uuid.uuid4())
        output_dir = os.path.join(st.session_state.temp_dir, task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # 1단계: 다운로드 및 음성 추출
        update_progress("영상 다운로드 및 음성 추출 중...", 20)
        file_paths = download_and_extract_audio(url, output_dir, update_progress)
        
        # 2단계: 텍스트 변환
        update_progress("음성을 텍스트로 변환 중...", 60)
        text_path, transcript_text = convert_audio_to_text(
            file_paths['audio'], 
            st.session_state.model, 
            update_progress
        )
        
        # 3단계: 결과 파일 준비
        update_progress("결과 파일 준비 중...", 90)
        
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
        
        update_progress("변환 완료!", 100)
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
    """변환 결과 표시"""
    st.markdown("---")
    st.subheader("📋 변환 결과")
    
    # 텍스트 결과 표시
    text_file = next((f for f in st.session_state.result_files if f['type'] == 'text'), None)
    if text_file and 'content' in text_file:
        st.markdown("**📝 변환된 텍스트:**")
        st.text_area(
            "변환 결과",
            value=text_file['content'],
            height=200,
            help="변환된 텍스트입니다. 복사하여 사용하세요."
        )
    
    # 다운로드 버튼들
    st.markdown("**📥 파일 다운로드:**")
    
    col1, col2, col3 = st.columns(3)
    
    for i, file_info in enumerate(st.session_state.result_files):
        if os.path.exists(file_info['path']):
            with open(file_info['path'], 'rb') as f:
                file_data = f.read()
            
            col = [col1, col2, col3][i % 3]
            with col:
                # 파일 타입에 따른 아이콘과 MIME 타입 설정
                if file_info['type'] == 'video':
                    icon = "🎥"
                    mime_type = "video/mp4"
                elif file_info['type'] == 'audio':
                    icon = "🎵"
                    mime_type = "audio/mpeg"
                else:  # text
                    icon = "📄"
                    mime_type = "text/plain"
                
                st.download_button(
                    label=f"{icon} {file_info['name']}",
                    data=file_data,
                    file_name=file_info['name'],
                    mime=mime_type
                )
    
    # 전체 ZIP 다운로드
    if len(st.session_state.result_files) > 1:
        zip_data = create_zip_file()
        if zip_data:
            st.download_button(
                label="📦 전체 파일 다운로드 (ZIP)",
                data=zip_data,
                file_name="youtube_conversion.zip",
                mime="application/zip"
            )
    
    # 새 변환 버튼
    if st.button("🔄 새로운 변환 시작"):
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