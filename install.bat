@echo off
chcp 65001 > nul
echo ========================================
echo 유튜브 텍스트 변환기 설치 스크립트
echo ========================================
echo.

echo [1/4] Python 설치 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요: https://python.org
    pause
    exit /b 1
)
echo ✅ Python 설치 확인 완료

echo.
echo [2/4] FFmpeg 설치 확인 중...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg이 설치되어 있지 않습니다.
    echo FFmpeg를 설치해주세요: https://ffmpeg.org/download.html
    echo 또는 winget install FFmpeg (Windows 10/11)
    pause
    exit /b 1
)
echo ✅ FFmpeg 설치 확인 완료

echo.
echo [3/4] Python 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치 실패
    pause
    exit /b 1
)
echo ✅ 패키지 설치 완료

echo.
echo [4/4] 설치 완료!
echo.
echo 🎉 유튜브 텍스트 변환기 설치가 완료되었습니다!
echo.
echo 실행 방법:
echo   1. run.bat 파일을 더블클릭하거나
echo   2. 명령어: python server.py
echo.
echo 브라우저에서 http://localhost:5000 접속
echo.
pause