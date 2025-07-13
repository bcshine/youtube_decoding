# YouTube 텍스트 변환기 배포 가이드

이 문서는 YouTube 텍스트 변환기를 배포하는 방법을 설명합니다.

## 목차
1. [로컬 실행](#로컬-실행)
2. [네트워크 배포](#네트워크-배포)
3. [클라우드 배포](#클라우드-배포)

---

## 로컬 실행

### 요구사항
- Python 3.8 이상
- 최소 4GB RAM (Whisper 모델용)
- 인터넷 연결

### 실행 방법

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **서버 실행**
   ```bash
   python server.py
   ```

3. **접속**
   - 브라우저에서 `http://localhost:5000` 접속

---

## 네트워크 배포

같은 Wi-Fi 네트워크의 다른 기기에서 접근 가능합니다.

### 실행 방법
```bash
.\run.bat
```

또는 수동으로:
```bash
python server.py
```

### 접속 방법
- 같은 Wi-Fi의 다른 기기에서 `http://[컴퓨터IP]:5000` 접속
- IP 확인: `ipconfig` 명령어 사용

### 장점
- 설정이 간단함
- 로컬 네트워크 내에서 빠른 속도

### 단점
- 같은 네트워크에서만 접근 가능
- 컴퓨터가 켜져 있어야 함

---

## 클라우드 배포

### ngrok을 이용한 임시 공개

1. **ngrok 설치**
   ```bash
   npm install -g ngrok
   ```

2. **서버 실행**
   ```bash
   python server.py
   ```

3. **터널 생성**
   ```bash
   ngrok http 5000
   ```

4. **공개 URL 사용**
   - ngrok이 제공하는 https URL로 전 세계 어디서나 접근 가능

### Heroku 배포

1. **Heroku CLI 설치**
   - https://devcenter.heroku.com/articles/heroku-cli

2. **프로젝트 준비**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Heroku 앱 생성 및 배포**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Railway 배포

1. **Railway 계정 생성**: https://railway.app
2. **GitHub 저장소 연결**
3. **자동 배포 완료**

### 장점
- 전 세계 어디서나 접근 가능
- HTTPS 자동 제공
- 무료 티어 제공

### 단점
- 인터넷 연결 필수
- 일부 서비스는 비용 발생

---