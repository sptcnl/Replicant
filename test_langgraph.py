from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import uuid, os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# 상태 정의: input_text를 입력받아 output_text를 생성할 예정
class State(TypedDict):
    input_text: str
    output_text: str

def call_model(state: State, config):
    # config에서 LLM 타입 가져오기(기본값: "openai")
    llm_type = config["configurable"]["llm"]["type"]

    # llm_type에 따라 LLM 인스턴스 생성 (예: openai, anthropic, huggingface 등)
    # 여기서는 예제로 llm_type이 "anthropic"이면 Anthropic API,
    # 아니면 OpenAI 기반 ChatOpenAI를 사용한다고 가정
    if llm_type == "anthropic":
        model = ChatOpenAI(model="claude-v1")  # 예: Anthropic Claude
    elif llm_type == "huggingface":
        model = ""
    elif llm_type == "gemini":
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            google_api_key=config["configurable"]["llm"]["api_key"],
            convert_system_message_to_human=True
        )
    elif llm_type == "openai":
        model = ChatOpenAI(model="gpt-4o-mini")  # 예: OpenAI 계열 모델
    else:
        raise ValueError
    
    user_input = state["input_text"]
    # 메시지 형태로 LLM 호출
    messages = [HumanMessage(content=state["input_text"])]
    response = model.invoke(messages)  # LLM 호출
    
    # 결과를 output_text에 반영
    return {"output_text": response.content}

# 그래프 구성
builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

thread_id = str(uuid.uuid4())
config = {
    "configurable": {
        "llm": {
            "type": "gemini",
            "api_key": gemini_api_key
        },
        "thread_id": thread_id  # thread_id 설정
    },
    "recursion_limit": 5,   # 옵션: recursion_limit 설정
}

initial_state = {"input_text": "하이", "output_text": ""}

# 그래프 실행
result = graph.invoke(initial_state, config=config)
print("최종 결과 상태:", result)