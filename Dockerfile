# Base image 설정
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt .

# 종속성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

RUN chmod +x server.py
# 컨테이너 실행 시 실행할 명령어
CMD [ "python", "server.py" ]
