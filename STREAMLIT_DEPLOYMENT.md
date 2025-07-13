# 🚀 Streamlit Cloud 배포 가이드

## 📋 개요
이 가이드는 유튜브 텍스트 변환기를 Streamlit Cloud에 배포하는 방법을 설명합니다.

## 🔧 필요한 파일들

### 1. 핵심 파일
- `app.py` - Streamlit 애플리케이션 메인 파일
- `requirements.txt` - Python 의존성
- `packages.txt` - 시스템 의존성 (ffmpeg)
- `.streamlit/config.toml` - Streamlit 설정
- `logo2.png` - 로고 이미지

### 2. 파일 구조
```
youtube_decoding/
├── app.py                    # Streamlit 앱
├── requirements.txt          # Python 패키지
├── packages.txt             # 시스템 패키지
├── logo2.png               # 로고
├── .streamlit/
│   └── config.toml         # Streamlit 설정
└── STREAMLIT_DEPLOYMENT.md # 이 가이드
```

## 🌐 Streamlit Cloud 배포 단계

### 1단계: GitHub 저장소 준비
1. GitHub에 새 저장소 생성
2. 프로젝트 파일들을 저장소에 업로드
3. 저장소를 public으로 설정

### 2단계: Streamlit Cloud 배포
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택:
   - Repository: `your-username/youtube-text-converter`
   - Branch: `main`
   - Main file path: `app.py`
5. "Deploy!" 클릭

### 3단계: 배포 확인
- 배포 과정에서 로그 확인
- 성공 시 앱 URL 제공됨
- 일반적으로 `https://your-app-name.streamlit.app` 형태

## ⚙️ 설정 설명

### requirements.txt
```txt
streamlit==1.28.1
yt-dlp==2023.7.6
openai-whisper==20230314
torch==2.0.1
torchaudio==2.0.2
numpy==1.24.3
scipy==1.10.1
ffmpeg-python==0.2.0
```

### packages.txt
```txt
ffmpeg
```

### .streamlit/config.toml
```toml
[global]
dataFrameSerialization = "legacy"

[server]
headless = true
port = $PORT
enableCORS = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
```

## 🎯 주요 기능

### Streamlit 버전의 특징
- **간단한 UI**: 직관적인 웹 인터페이스
- **실시간 진행률**: 변환 과정 실시간 표시
- **파일 다운로드**: 텍스트 및 오디오 파일 다운로드
- **ZIP 압축**: 전체 파일 일괄 다운로드
- **반응형 디자인**: 모바일 친화적

### 지원 기능
- ✅ 유튜브 URL 유효성 검사
- ✅ 음성 추출 및 텍스트 변환
- ✅ 실시간 진행률 표시
- ✅ 결과 파일 다운로드
- ✅ 에러 처리 및 사용자 피드백

## 🔍 로컬 테스트

배포 전 로컬에서 테스트:

```bash
# 의존성 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 🚨 주의사항

### 1. 리소스 제한
- Streamlit Cloud는 무료 플랜에서 리소스 제한이 있음
- 큰 파일이나 긴 영상은 처리 시간이 오래 걸릴 수 있음
- 메모리 사용량 주의 (1GB 제한)

### 2. 파일 저장
- 임시 파일은 세션 종료 시 삭제됨
- 영구 저장이 필요한 경우 외부 스토리지 사용 권장

### 3. 보안
- 민감한 정보는 Streamlit Secrets 사용
- API 키 등은 환경 변수로 관리

## 🔧 문제 해결

### 일반적인 문제들

1. **ffmpeg 오류**
   - `packages.txt`에 `ffmpeg` 추가 확인
   - 배포 로그에서 설치 확인

2. **메모리 부족**
   - Whisper 모델을 더 작은 버전으로 변경 (`tiny`, `small`)
   - 파일 크기 제한 추가

3. **배포 실패**
   - requirements.txt 버전 호환성 확인
   - 배포 로그 상세 확인

## 📞 지원

문제가 발생하면:
1. Streamlit Cloud 배포 로그 확인
2. GitHub Issues 확인
3. Streamlit Community Forum 참조

## 🎉 완료!

배포가 완료되면 전 세계 어디서나 유튜브 텍스트 변환기를 사용할 수 있습니다!

**배포 URL 예시**: `https://youtube-text-converter.streamlit.app`