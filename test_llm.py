import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

snapshot_download(
    repo_id="naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B",
    token=HF_TOKEN,
    local_dir="./HyperCLOVA-X-SEED-1.5B",
    ignore_patterns=["*.msgpack", "*.h5", "*.tar"],  # 불필요한 파일 제외
    resume_download=True
)

model_path = "./HyperCLOVA-X-SEED-1.5B"
model = AutoModelForCausalLM.from_pretrained(model_path, token=HF_TOKEN)
tokenizer = AutoTokenizer.from_pretrained(model_path)
while True:
    user_input = input("대화를 시작하세요, 대화를 끝내시려면 끝 이라고 입력해주세요: ")

    if user_input == "끝":
        break

    chat = [
        {"role": "system", "content": "너는 네이버의 AI 언어모델 CLOVA X야. 오늘은 2025년 6월 4일이야."},
        {"role": "user", "content": user_input}
    ]

    inputs = tokenizer.apply_chat_template(chat, add_generation_prompt=True, return_tensors="pt")

    output_ids = model.generate(
        inputs,
        max_new_tokens=500,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        do_sample=True,
        temperature=0.7
    )

    print(tokenizer.decode(output_ids[0], skip_special_tokens=True))