from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
import os, time, torch, uuid

# HyperCLOVA-X 초기화 --------------------------------------------------------
class HyperCLOVA_X_System:
    def __init__(self):
        self._init_model()
        self._warmup_model()

    def _init_model(self):
        """모델 초기화 및 최적화 설정"""
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        # 양자화 설정
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        # 모델 로드
        self.model = AutoModelForCausalLM.from_pretrained(
            "./HyperCLOVA-X-SEED-1.5B",
            torch_dtype=torch.bfloat16,
            device_map="auto",
            quantization_config=bnb_config,
            token=os.getenv("HF_TOKEN")
        )
        
        # 토크나이저 설정
        self.tokenizer = AutoTokenizer.from_pretrained("./HyperCLOVA-X-SEED-1.5B")
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def _warmup_model(self):
        """모델 워밍업 프로세스"""
        warmup_prompt = self.tokenizer("안녕", return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            _ = self.model.generate(**warmup_prompt, max_new_tokens=10)
        torch.cuda.empty_cache()

# LangGraph 상태 관리 시스템 -------------------------------------------------
class State(TypedDict):
    input_text: str
    output_text: str
    metadata: dict

clova_system = HyperCLOVA_X_System()

def call_model(state: State, config):
    """LangGraph 노드용 모델 호출 함수"""
    start_time = time.time()
    
    # 입력 처리
    user_input = state["input_text"]
    system_message = {"role": "system", "content": "너는 네이버의 AI 언어모델 CLOVA X야. 오늘은 2025년 6월 4일이야."}
    
    # 토큰화
    messages = [system_message, {"role": "user", "content": user_input}]
    input_ids = clova_system.tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(clova_system.model.device)
    
    # 텍스트 생성
    with torch.no_grad():
        output_ids = clova_system.model.generate(
            input_ids,
            max_new_tokens=256,
            temperature=0.4,
            top_p=0.9,
            do_sample=True,
            eos_token_id=clova_system.tokenizer.eos_token_id,
            pad_token_id=clova_system.tokenizer.pad_token_id
        )
    
    # 결과 처리
    response = clova_system.tokenizer.decode(
        output_ids[0][input_ids.shape[1]:], 
        skip_special_tokens=True
    )
    
    return {
        "output_text": response,
        "metadata": {
            "execution_time": time.time() - start_time,
            "model": "HyperCLOVA-X-1.5B",
            "config": config
        }
    }

# 실행 그래프 구성 -----------------------------------------------------------
builder = StateGraph(State)
builder.add_node("clova_x", call_model)
builder.add_edge(START, "clova_x")
builder.add_edge("clova_x", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# 테스트용 대화 인터페이스 ------------------------------------------------------------
def chat_interface():
    """대화 실행 루프"""
    while True:
        user_input = input("\n사용자 입력 (종료: '끝'): ")
        if user_input.lower() == "끝":
            break
        
        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
                "llm": "hyperclova"
            }
        }
        
        result = graph.invoke(
            {"input_text": user_input, "output_text": "", "metadata": {}},
            config=config
        )
        
        print(f"\nCLOVA X: {result['output_text']}")
        print(f"메타데이터: {result['metadata']}")

if __name__ == "__main__":
    chat_interface()