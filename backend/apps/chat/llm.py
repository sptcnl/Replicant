from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.redis import RedisSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import os, logging

gemini_api_key = os.getenv("GEMINI_API_KEY")
in_memory_store = InMemoryStore()  # 장기 메모리 저장소 초기화


# 상태 정의
class State(TypedDict):
    input_text: str
    output_text: str
    history: list[dict]


def should_summarize(state: State, config) -> str:
    """5턴마다 요약 생성 조건 확인"""
    return "summarize" if len(state.get("history", [])) % 5 == 0 else "end"


def summarize_history(state: State, config):
    """요약 생성 노드"""
    llm_type = config["configurable"]["llm"]["type"]
    user_id = config["configurable"]["user_id"]
    session_id = config["configurable"]["session_id"]

    # 메타데이터 조회
    namespace_meta = (user_id, session_id, "metadata")
    metadata = in_memory_store.get(namespace_meta, "character")
    logging.info(f"character_metadata: {metadata}")
    metadata_val = metadata.value


    # 모델 초기화
    if llm_type == "gemini":
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=config["configurable"]["llm"]["api_key"]
        )

    # 요약 프롬프트
    summary_prompt = f"""
    [요약 규칙]
    1. 다음 대화를 3문장 이내로 요약
    2. 주요 사건/감정/목표 중심으로 작성
    3. {metadata['name']}의 행동 강조
    4. 최종 관계가 어떻게 됐는지 정리

    [대화 기록]
    {state['history'][-5:]}  # 최근 5턴
    """

    response = model.invoke([HumanMessage(content=summary_prompt)])
    summary = response.content

    # 요약 저장
    namespace_sum = (user_id, session_id, "summaries")
    old = in_memory_store.get(namespace_sum, "all_summaries")
    summaries = old.value + [summary] if old else [summary]
    in_memory_store.put(namespace_sum, "all_summaries", summaries)

    logging.info(f"[디버그: summaries 저장 완료] {in_memory_store.search(namespace_sum)}")

    return {"summary": summary}


def call_model(state: State, config):
    logging.info(f"config: {config}")
    llm_type = config["configurable"]["llm"]["type"]
    user_id = config["configurable"]["user_id"]
    session_id = config["configurable"]["session_id"]

    # 메타데이터 조회
    namespace_meta = (str(user_id), str(session_id), "metadata")
    metadata = in_memory_store.get(namespace_meta, "character")
    logging.info(f"character_metadata: {metadata}")
    metadata_val = metadata.value

    # 최신 요약 불러오기
    namespace_sum = (user_id, session_id, "summaries")
    summaries = in_memory_store.get(namespace_sum, "all_summaries")
    latest_summary = summaries.value[-1] if summaries else "요약 정보 없음"

    # 모델 초기화
    if llm_type == "gemini":
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=config["configurable"]["llm"]["api_key"]
        )

    # 대화 메시지 구성
    messages = []
    for turn in state.get("history", []):
        messages.extend([
            HumanMessage(content=turn["user"]),
            AIMessage(content=turn["ai"])
        ])

    system_msg = f"""
    [최근 대화 요약]
    {latest_summary}

    너는 이 캐릭터이고, 나와 이 설정에 맞춰 연기해줘.
    [캐릭터 설정]
    - 당신은 {metadata['name']} 역할을 맡았습니다.
    - 당신의 성격: {', '.join(metadata['personality'])}
    - 반드시 이 역할에 충실해야 합니다.
    - 다른 캐릭터의 말을 흉내내지 마세요.
    - 캐릭터 설정이 아닌 시나리오가 바뀌면 자연스럽게 진행하세요.

    [현재 시나리오]
    {metadata['scenario']}
    """

    messages.append(HumanMessage(content=system_msg))
    messages.append(HumanMessage(content=state["input_text"]))

    response = model.invoke(messages)

    # 새로운 history 저장
    new_history = state.get("history", []) + [
        {"user": state["input_text"], "ai": response.content}
    ][-30:]  # 최대 30턴만 유지

    return {
        "output_text": response.content,
        "history": new_history
    }


# 그래프 정의
builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_node("summarize", summarize_history)
builder.add_edge(START, "call_model")
builder.add_conditional_edges(
    "call_model", should_summarize,
    {
        "summarize": "summarize",
        "end": END
    }
)
builder.add_edge("summarize", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)