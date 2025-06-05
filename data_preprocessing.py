import os, re, json, time
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API 키 설정
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

def generate_prompt(message: str) -> str:
    i = 0
    while True:
        i += 1
        try:
            print(str(i)+"번째 시도")
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 사용자 메시지의 적절한 이전 질문 혹은 이전 대화를 친구/동료 시점으로 50자 이내 한국어로 생성해주세요. (출력 예시: 상대방이 고기 먹은것을 자랑한다) 메시지: '{message}'",
            )
            print(response.text.strip() + "\n" + message)
            return response.text.strip()
        except Exception as e:
            print(e)
            time.sleep(5)
    # return "대화를 시작해주세요"

# 카톡 메세지 전처리
# 보낸이 이름 패턴 (김나희, 나희 모두 포함)
senders = ['김나희', '나희']
files = ['ptday412.txt', 'ptday412_develop.txt']
results = []

# 카카오톡 메시지 패턴
pattern = re.compile(r'^\[(.*?)\] \[(.*?)\] (.*)$')

# URL 패턴
url_pattern = re.compile(r'https?://\S+')
# 이메일 패턴
email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

for file in files:
    with open(file, encoding='utf-8') as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                sender, ts, message = match.groups()
                if any(s in sender for s in senders):
                    # 메시지에서 URL, 이메일 추출
                    urls = url_pattern.findall(message)
                    emails = email_pattern.findall(message)
                    # 메시지에서 URL, 이메일 제거
                    message_no_url_email = url_pattern.sub('', message)
                    message_no_url_email = email_pattern.sub('', message_no_url_email).strip()
                    # 1. 메시지가 오직 링크/이메일만 있는 경우: 패스
                    if message_no_url_email == '' and (urls or emails):
                        continue
                    # 2. 메시지에 링크/이메일 + 텍스트가 있으면: 텍스트만 저장
                    elif message_no_url_email:
                        results.append(
                            {
                                "prompt": generate_prompt(message_no_url_email.strip()),
                                "completion": message_no_url_email.strip()
                            }
                        )
                    # 3. 메시지에 링크/이메일 없고 텍스트만 있으면: 텍스트 저장
                    elif not (urls or emails) and message:
                        results.append(
                            {
                                "prompt": generate_prompt(message.strip()),
                                "completion": message.strip()
                            }
                        )

# 결과 저장
json_data = json.dumps(results, ensure_ascii=False, indent=2)
with open("my_final_ptday_message.json", "w", encoding="utf-8") as f:
    f.write(json_data)


# 슬랙 메세지 전처리
file_path = 'my_messages_in_lounge_channel.json'
results = []

# 패턴 정의
# 1. ( <https://...> ) 또는 ( <https://...|...> ) 괄호 전체 제거
paren_slack_url_pattern = re.compile(r'\(<https?://[^>|]+(?:\|[^>]+)?>\)')
# 2. 슬랙 링크만 남은 경우(<https://...|...> 또는 <https://...>) 제거
slack_url_pattern = re.compile(r'<https?://[^>|]+(?:\|[^>]+)?>')
# 3. 일반 URL 제거
url_pattern = re.compile(r'https?://\S+')
# 4. 이메일 제거
email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
# 5. 슬랙 이모티콘 제거
emoji_pattern = re.compile(r':[a-zA-Z0-9_+\-]+:')

def clean_message(text):
    # 1. ( <https://...> ) 괄호 전체 제거
    text = paren_slack_url_pattern.sub('', text)
    # 2. 슬랙 링크 제거
    text = slack_url_pattern.sub('', text)
    # 3. 일반 URL 제거
    text = url_pattern.sub('', text)
    # 4. 이메일 제거
    text = email_pattern.sub('', text)
    # 5. 슬랙 이모티콘 제거
    text = emoji_pattern.sub('', text)
    # 6. 불필요한 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text

with open(file_path, encoding='utf-8') as f:
    data = json.load(f)
    if isinstance(data, list):
        messages = data
    elif isinstance(data, dict):
        messages = data.get('messages', [])
    else:
        messages = []

    for msg in messages:
        if msg.get('type') == 'message' and 'text' in msg:
            text = msg['text']
            if text and text.strip():
                cleaned = clean_message(text)
                if cleaned:
                    results.append(
                        {
                            "prompt": generate_prompt(cleaned),
                            "completion": cleaned
                        }
                    )

# 결과 저장
json_data = json.dumps(results, ensure_ascii=False, indent=2)
with open("my_final_slack_message.json", "w", encoding="utf-8") as f:
    f.write(json_data)