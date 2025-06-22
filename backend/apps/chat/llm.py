from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import uuid, os

gemini_api_key = os.getenv("GEMINI_API_KEY")
in_memory_store = InMemoryStore()  # 장기 메모리 저장소 초기화

# 상태 정의: metadata 제거
class State(TypedDict):
    input_text: str
    output_text: str
    history: list[dict]

def should_summarize(state: State, config) -> str:
    """5턴마다 요약 생성 조건 확인"""
    return "summarize" if len(state.get("history", [])) % 5 == 0 else "end"

def summarize_history(state: State, config):
    """대화 기록 요약 생성 노드"""
    llm_type = config["configurable"]["llm"]["type"]
    
    # 메타데이터 조회
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "metadata")
    metadata = in_memory_store.get(namespace, "character").value
    
    # 모델 초기화
    if llm_type == "gemini":
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=config["configurable"]["llm"]["api_key"]
        )
    
    # 요약 생성 프롬프트
    summary_prompt = f"""
    [요약 규칙]
    1. 다음 대화를 3문장 이내로 요약
    2. 주요 사건/감정/목표 중심으로 작성
    3. {metadata['name']}의 행동 강조
    4. 최종 관계가 어떻게 됐는지 정리
    
    [대화 기록]
    {state['history'][-5:]}  # 최근 5턴만 요약
    """
    
    # 요약 생성
    response = model.invoke([HumanMessage(content=summary_prompt)])
    summary = response.content
    
    # 장기 메모리에 요약 저장
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "summaries")
    summaries = in_memory_store.get(namespace, "all_summaries")
    if summaries:
        summaries = summaries.value + [summary]  # 기존 요약에 추가
    else:
        summaries = [summary]
    in_memory_store.put(namespace, "all_summaries", summaries)
    print(f"in_memory_store: {in_memory_store.search(namespace)}")
    
    return {"summary": summary}

def call_model(state: State, config):
    llm_type = config["configurable"]["llm"]["type"]
    
    # 메타데이터 조회
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "metadata")
    metadata = in_memory_store.get(namespace, "character").value  # 저장소에서 조회
    summaries = in_memory_store.get(namespace, "all_summaries")
    latest_summary = summaries.value[-1] if summaries else "요약 정보 없음"
    
    # 모델 초기화 (기존 코드와 동일)
    if llm_type == "gemini":
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=config["configurable"]["llm"]["api_key"]
        )
    
    # 메시지 구성
    messages = []
    for turn in state.get("history", []):
        messages.extend([
            HumanMessage(content=turn["user"]),
            AIMessage(content=turn["ai"])
        ])
    
    # 시스템 메시지에 메타데이터 반영
    system_msg = f"""
    [최근 대화 요약]
    {latest_summary}

    너는 이 캐릭터이고, 나와 이 설정에 맞춰 연기해줘.
    [캐릭터 설정]
    - 당신은 {metadata['name']} 역할을 맡았습니다.
    - 당신의 성격: {', '.join(metadata['personality'])}
    - 반드시 이 역할에 충실해야 합니다.
    - 다른 캐릭터의 말을 흉내내지 마세요.
    - 캐릭터 설정이 아닌 시나리오가 바뀌게 되면 캐묻지 말고 자연스럽게 진행해
    
    [현재 시나리오]
    {metadata['scenario']}
    """
    messages.append(HumanMessage(content=system_msg))
    messages.append(HumanMessage(content=state["input_text"]))
    
    response = model.invoke(messages)
    
    new_history = state.get("history", []) + [
        {"user": state["input_text"], "ai": response.content}
    ][-30:]  # 최근 30개만 유지
    
    return {
        "output_text": response.content,
        "history": new_history
    }

# 그래프 구성
builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_node("summarize", summarize_history)
builder.add_edge(START, "call_model")
builder.add_conditional_edges(  # 조건부 엣지 추가
    "call_model",
    should_summarize,
    {
        "summarize": "summarize",
        "end": END
    }
)
builder.add_edge("summarize", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)