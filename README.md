# Replicant
![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-092E20?style=for-the-badge&logo=django&logoColor=white&color=7f2d2d)
![Django Channels](https://img.shields.io/badge/Django_Channels-092E20?style=for-the-badge&logo=django&logoColor=white&color=092E20)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![nginx](https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

## 📑 Index

### 🚀 [Main Features](#-main-features-1)
- [AI와의 실시간 채팅](#-가족-등록-및-관리-기능)

### 📖 [How to Use](#-how-to-use-1)
- [.env 파일 구성](#what-should-go-into-a-env-file)
- [Docker 및 로컬 개발 환경 실행 방법]()

<br><br>

## 🚀 Main Features
[-> 프로젝트 실행 영상(업로드 예정)]()

### 💬 AI와의 실시간 채팅
**Family Registration & Management**

- 실시간 채팅 기능은 Django Channels를 활용해 구현했으며, Redis를 사용하여 최근 30턴의 채팅 기록과 그 요약을 별도로 저장하고 불러옵니다. 대화의 자연스러운 흐름과 효율적인 관리가 가능하도록 LangGraph라는 LLM(대형 언어 모델) 프레임워크도 함께 사용하고 있습니다.
  <br> <br>
  _The real-time chat functionality is implemented using Django Channels, and Redis is used to separately store and retrieve the latest 30 turns of chat history along with their summaries. To ensure natural conversation flow and efficient management, the system also uses LangGraph, a large language model (LLM) framework._

<br><br>

## 📖 How to use

### What should go into a .env file?
Your .env file should contain environment variables such as contract addresses required for your application.
<br><br>
<b>Here’s an example:</b>
```
# ./.env
HF_TOKEN="YOUR_HF_TOKEN"
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```
```
# ./backend/.env
DEV_SECRET_KEY="DEV_SECRET_KEY"
DEV_DB_NAME="DEV_DB_NAME"
DEV_DB_USER="DEV_DB_USER"
DEV_DB_PASSWORD="DEV_DB_PASSWORD"
DEV_DB_HOST="DEV_DB_HOST"
DEV_DB_PORT="DEV_DB_PORT"
GEMINI_API_KEY="GEMINI_API_KEY"
API_HOST="API_HOST"
PRIVATE_IP="PRIVATE_IP"
```
```
# ./frontend/.env
VITE_API_HOST="localhost"
```

### How to run with Docker & Local Development
#### Backend
1. Open a terminal and navigate to the backend directory:
```
cd ./docker/dev
```
2. Build the Docker image and start the container:
```
docker-compose up --build
```
- Make sure your .env file is correctly set up in the same directory.

#### Frontend
1. Open a new terminal and move to the frontend directory:
```
cd ./frontend
```
2. Install dependencies:
```
npm install
```
3. Start the development server:
```
npm run dev
```
- The frontend should be accessible by default at http://localhost:5173 (or as configured).

<b>Tips:</b>

You may need to adjust ports in the Docker or Vite config files if defaults conflict.

Ensure both backend and frontend .env files exist in their respective directories before running.