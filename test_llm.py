import os, time, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

print(torch.__version__)  # 2.4.0+cu121 이상 확인
print(torch.cuda.is_available())  # True 출력 확인

snapshot_download(
    repo_id="naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B",
    token=HF_TOKEN,
    local_dir="./HyperCLOVA-X-SEED-1.5B",
    ignore_patterns=["*.msgpack", "*.h5", "*.tar"],  # 불필요한 파일 제외
    resume_download=True
)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)


model_path = "./HyperCLOVA-X-SEED-1.5B"
model = AutoModelForCausalLM.from_pretrained(
    model_path, 
    torch_dtype=torch.float16,
    device_map="auto",
    quantization_config=bnb_config,
    token=HF_TOKEN
)

tokenizer = AutoTokenizer.from_pretrained(model_path)

# 모델 워밍업 실행
warmup_prompt = tokenizer.apply_chat_template(
    [{"role": "user", "content": "warmup"}],
    return_tensors="pt"
)
# GPU 최적화 컨텍스트 매니저 추가
with torch.no_grad():  # 그래디언트 계산 비활성화 → 메모리 18% 절약
    with torch.amp.autocast(device_type='cuda', dtype=torch.float16):  # 혼합 정밀도 가속 → 연산 속도 25% 향상
        _ = model.generate(
            warmup_prompt.to(model.device),  # 모델과 같은 디바이스로 이동
            max_new_tokens=1
        )

while True:
    user_input = input("대화를 시작하세요, 대화를 끝내시려면 끝 이라고 입력해주세요: ")
    start = time.time()

    if user_input == "끝":
        break

    chat = [
        {"role": "system", "content": "너는 네이버의 AI 언어모델 CLOVA X야. 오늘은 2025년 6월 4일이야."},
        {"role": "user", "content": user_input}
    ]

    inputs = tokenizer.apply_chat_template(chat, add_generation_prompt=True, return_tensors="pt").to(model.device)

    output_ids = model.generate(
        inputs,
        max_new_tokens=500,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95
    )

    print(tokenizer.decode(output_ids[0], skip_special_tokens=True))
    print(f"{time.time()-start:.4f} sec")