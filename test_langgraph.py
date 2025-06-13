from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import uuid, os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# 상태 정의: input_text를 입력받아 output_text를 생성할 예정
class State(TypedDict):
    input_text: str
    output_text: str
    history: list[dict]
    metadata: dict

def call_model(state: State, config):
    """llm 부르는 node"""
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
            google_api_key=config["configurable"]["llm"]["api_key"]
        )
    elif llm_type == "openai":
        model = ChatOpenAI(model="gpt-4o-mini")  # 예: OpenAI 계열 모델
    else:
        raise ValueError(f"지원하지 않는 모델: {llm_type}")
    
    # 메시지 형태로 LLM 호출
    # 히스토리를 메시지로 변환
    messages = []
    for turn in state.get("history", []):
        messages.append(HumanMessage(content=turn["user"]))
        messages.append(AIMessage(content=turn["ai"]))
    
    # 현재 입력 추가
    messages.append(HumanMessage(
        content=state["input_text"]
    ))
    messages.append(HumanMessage(
        content=f'이건 너의 이름, 나이, 성격 등의 정보야. 이 정보를 토대로 나와 역할놀이 해줘: {state["metadata"]}'
    ))
    print("messages: ", messages)
    response = model.invoke(messages)  # LLM 호출
    
    # 결과를 output_text에 반영
    return {
        "output_text": response.content,
        "history": state.get("history", []) + [
            {"user": state["input_text"], "ai": response.content}
        ]
    }

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

current_state = {
    "input_text": "", 
    "output_text": "", 
    "history": [], 
    "metadata": {
        "character": {
        "name": "Dr. Watson",
        "personality": ["날카로운 관찰력", "의학 전문가"]
        },
        "scenario": "19세기 런던 탐정물, 베이커가 221B를 배경으로 한다. 왓슨은 나(셜록)의 탐정 조수."
    }
}

while True:
    print(thread_id, config)
    user_input = input("대화를 해주세요 (종료 시 'end'):")
    if user_input.lower() == "end":
        break
    current_state["input_text"] = user_input
    # 그래프 실행
    result = graph.invoke(current_state, config=config)
    print("AI:", result["output_text"])
    current_state = {  # 새로운 상태로 교체
        "input_text": "",
        "output_text": "",
        "history": result["history"],
        "metadata": result.get("metadata", current_state["metadata"])
    }