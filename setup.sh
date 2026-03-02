#!/bin/bash
# AgileClaw 한 번에 설치
set -e

echo "🦾 AgileClaw setup..."

# venv 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt -q

# Playwright 브라우저 설치
playwright install chromium

# config 파일 생성
if [ ! -f config.yaml ]; then
    cp config.example.yaml config.yaml
    echo "📝 config.yaml 생성됨 — Telegram 토큰과 Claude API 키를 입력해주세요"
fi

# memory 폴더 생성
mkdir -p memory

echo "✅ 설치 완료!"
echo ""
echo "다음 단계:"
echo "1. config.yaml 편집 (bot_token, api_key 입력)"
echo "2. source venv/bin/activate"
echo "3. python main.py"
