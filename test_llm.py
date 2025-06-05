import os, time, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# PyTorch 설정 최적화
torch.backends.cuda.enable_mem_efficient_sdp(True)  # 메모리 효율적 어텐션

print(f"PyTorch: {torch.__version__}, CUDA: {torch.version.cuda}")
print(f"GPU available: {torch.cuda.is_available()}")

# 모델 다운로드 (기존 코드 유지)
snapshot_download(
    repo_id="naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B",
    token=HF_TOKEN,
    local_dir="./HyperCLOVA-X-SEED-1.5B",
    ignore_patterns=["*.msgpack", "*.h5", "*.tar"],
    resume_download=True
)

# 양자화 설정 업그레이드
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16  # float16 → bfloat16로 변경
)

# 모델 로드 최적화
model_path = "./HyperCLOVA-X-SEED-1.5B"
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    quantization_config=bnb_config,
    token=HF_TOKEN
)

# 토크나이저 설정
tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token  # 패딩 토큰 명시적 설정

# 시스템 프롬프트 사전 토큰화
system_prompt = tokenizer.apply_chat_template(
    [{"role": "system", "content": "너는 네이버의 AI 언어모델 CLOVA X야. 오늘은 2025년 6월 4일이야."}],
    add_generation_prompt=True,
    return_tensors="pt"
).to(model.device)

# 확장 워밍업 프로세스
warmup_inputs = torch.cat([system_prompt, tokenizer.encode("warmup", return_tensors="pt").to(model.device)], dim=-1)
with torch.no_grad(), torch.cuda.amp.autocast(dtype=torch.bfloat16):
    _ = model.generate(
        warmup_inputs,
        max_new_tokens=10,
        do_sample=False,
        use_cache=True
    )
torch.cuda.empty_cache()  # 워밍업 후 캐시 정리

# 대화 루프
while True:
    user_input = input("\n대화를 시작하세요 (종료: '끝' 입력): ")
    if user_input.lower() == "끝":
        break
    
    start_time = time.time()
    
    # 사용자 입력 토큰화
    user_input_ids = tokenizer.apply_chat_template(
        [{"role": "user", "content": user_input}],
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)
    
    # 전체 입력 조합
    input_ids = torch.cat([system_prompt, user_input_ids], dim=-1)
    
    # 최적화된 생성 파라미터
    output_ids = model.generate(
        input_ids,
        max_new_tokens=256,  # 500 → 256으로 축소
        temperature=0.4,     # 0.7 → 0.4 조정
        top_p=0.9,           # 0.95 → 0.9 최적화
        do_sample=True,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        repetition_penalty=1.15,  # 반복 제어 추가
        use_cache=True,
        output_attentions=False,
        output_hidden_states=False
    )
    
    # 결과 디코딩 및 출력
    response = tokenizer.decode(
        output_ids[0][input_ids.shape[1]:], 
        skip_special_tokens=True
    )
    print(f"\nCLOVA X: {response}")
    print(f"응답 시간: {time.time()-start_time:.2f}초")