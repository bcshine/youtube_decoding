# 🎬 유튜브 텍스트 변환기

유튜브 영상의 음성을 텍스트로 변환하는 웹 애플리케이션입니다.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## ✨ 주요 기능

- 🎥 **유튜브 영상 다운로드**: URL만 입력하면 자동으로 영상 다운로드
- 🎵 **음성 추출**: 영상에서 고품질 음성 파일 추출
- 📝 **텍스트 변환**: OpenAI Whisper를 사용한 정확한 음성-텍스트 변환
- 📊 **실시간 진행률**: 변환 과정을 실시간으로 확인
- 📁 **파일 다운로드**: 변환된 텍스트와 음성 파일 다운로드
- 🌐 **웹 인터페이스**: 직관적이고 사용하기 쉬운 웹 UI

## 🚀 빠른 시작

### 🌐 온라인 사용 (권장)

**Streamlit Cloud에서 바로 사용하기:**
👉 [유튜브 텍스트 변환기 웹앱](https://your-app-name.streamlit.app)

### 💻 로컬 실행

#### Streamlit 버전 (권장)
```bash
# 1. 저장소 클론
git clone <repository-url>
cd youtube_decoding

# 2. 의존성 설치
pip install -r requirements.txt

# 3. Streamlit 앱 실행
streamlit run app.py
```

#### Flask 버전
```bash
# 1. 자동 설치 및 실행 (Windows)
install.bat
run.bat

# 2. 수동 실행
python server.py
```

## 📋 시스템 요구사항

- **Python**: 3.8 이상
- **FFmpeg**: 음성 처리를 위해 필요
- **메모리**: 최소 4GB RAM (Whisper 모델 로딩)
- **저장공간**: 임시 파일을 위한 충분한 공간

## 🔧 기술 스택

### Streamlit 버전 (메인)
- **프레임워크**: Streamlit
- **AI 모델**: OpenAI Whisper
- **영상 처리**: yt-dlp, FFmpeg
- **배포**: Streamlit Cloud

### Flask 버전 (레거시)
- **백엔드**: Flask, Python
- **프론트엔드**: HTML, CSS, JavaScript

## 📁 프로젝트 구조

```
youtube_decoding/
├── app.py                    # Streamlit 앱 (메인)
├── server.py                 # Flask 서버 (레거시)
├── index.html               # Flask 웹 인터페이스
├── requirements.txt         # Python 의존성
├── packages.txt            # 시스템 의존성 (Streamlit Cloud용)
├── .streamlit/
│   ├── config.toml         # Streamlit 로컬 설정
│   └── config_cloud.toml   # Streamlit Cloud 설정
├── install.bat             # 자동 설치 스크립트
├── run.bat                # 실행 스크립트
├── logo2.png              # 로고 이미지
├── README.md              # 프로젝트 문서
├── DEPLOYMENT.md          # Flask 배포 가이드
└── STREAMLIT_DEPLOYMENT.md # Streamlit 배포 가이드
```

## 🌐 배포 옵션

### 1. Streamlit Cloud (권장)
- **장점**: 무료, 간단한 배포, 자동 업데이트
- **가이드**: [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)
- **URL**: `https://your-app-name.streamlit.app`

### 2. 로컬 네트워크
- Flask 버전으로 로컬 네트워크에서 접근 가능
- 같은 WiFi의 다른 기기에서 접속 가능

### 3. 기타 클라우드
- 자세한 배포 방법은 [DEPLOYMENT.md](DEPLOYMENT.md) 참조

## 🎯 사용법

### Streamlit 버전
1. 웹앱 접속: https://your-app-name.streamlit.app
2. 유튜브 URL 입력
3. "🚀 변환 시작" 버튼 클릭
4. 실시간 진행률 확인
5. 변환 완료 후 파일 다운로드

### Flask 버전
1. 브라우저에서 `http://localhost:5000` 접속
2. 유튜브 URL 입력
3. "변환 시작" 버튼 클릭
4. 진행률 확인 후 결과 파일 다운로드

## ⚠️ 주의사항

- 저작권이 있는 콘텐츠는 개인적 용도로만 사용
- 대용량 파일 처리 시 시간이 오래 걸릴 수 있음
- 인터넷 연결이 필요 (유튜브 다운로드)
- Streamlit Cloud는 무료 플랜에서 리소스 제한이 있음

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

## 🙏 감사의 말

- [OpenAI Whisper](https://github.com/openai/whisper) - 음성 인식 모델
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 유튜브 다운로더
- [Streamlit](https://streamlit.io/) - 웹 앱 프레임워크
- [Flask](https://flask.palletsprojects.com/) - 웹 프레임워크