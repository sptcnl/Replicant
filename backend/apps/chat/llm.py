from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis import RedisSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import os, json, redis, logging
from .models import Chat

gemini_api_key = os.getenv("GEMINI_API_KEY")

with RedisSaver.from_conn_string("redis://channels_redis:6379") as checkpointer:
    checkpointer.setup()

# Redis 클라이언트
redis_client = redis.Redis.from_url("redis://channels_redis:6379")

def save_chat(thread_id: str, chat_history: list):
    """
    thread_id별 대화기록 저장
    30턴만 유지
    chat_history: [ {"role": "user", "content": "안녕하세요"}, ... ]
    """
    key = f"chat:{thread_id}"
    redis_client.set(key, json.dumps(chat_history))
    return True

def save_chat_to_rdb(room_id: str, chat: dict):
    user_chat = chat["U"]
    ai_chat = chat["A"]

    Chat.objects.create(room_id=room_id, content=user_chat, sender_type="U")
    Chat.objects.create(room_id=room_id, content=ai_chat, sender_type="A")

def load_chat(thread_id: str):
    """
    저장된 대화기록 불러오기
    """
    key = f"chat:{thread_id}"
    data = redis_client.get(key)
    if data is None:
        return []
    return json.loads(data)

def save_summary(thread_id: str, summary: str):
    """
    thread_id별 요약 텍스트 저장
    """
    key = f"summary:{thread_id}"
    redis_client.set(key, summary)
    return True

def load_summary(thread_id: str):
    """
    요약 텍스트 불러오기
    """
    key = f"summary:{thread_id}"
    data = redis_client.get(key)
    if data is None:
        return None
    return data.decode()

def save_metadata(thread_id: str, metadata: dict):
    """
    thread_id별 메타데이터 저장
    """
    key = f"meta:{thread_id}"
    redis_client.set(key, json.dumps(metadata))
    return True

def load_metadata(thread_id: str):
    """
    메타데이터 불러오기
    """
    key = f"meta:{thread_id}"
    data = redis_client.get(key)
    if data is None:
        return {}
    return json.loads(data)


# 상태 정의
class State(TypedDict):
    input_text: str
    output_text: str
    history: list[dict]


def summarize_history(state: State, config):
    """요약 생성 노드"""
    try:
        llm_type = config["configurable"]["llm"]["type"]
        user_id = config["configurable"]["user_id"]
        thread_id = config["configurable"]["thread_id"]

        # 메타데이터 조회
        metadata = load_metadata(thread_id)
        logging.info(f"character_metadata: {metadata}")
        # metadata_val = metadata.values
        # logging.info(f"character_metadata_val: {metadata_val}")


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
        logging.info(f"llm summary response: {response}")
    except Exception as e:
        error_msg = str(e)
        logging.error(f"llm summary response error: {error_msg}")
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            return {
                "error_code": 429,
                "error_message": "API rate limit exceeded"
            }
        return e

    summary = response.content

    # 요약 저장
    is_saved = save_summary(thread_id, summary)

    if is_saved:
        logging.info(f"[디버그: summaries 저장 완료] {thread_id}: {summary}")

    return {"summary": summary}


def call_model(state: State, config):
    try:
        logging.info(f"config: {config}")
        llm_type = config["configurable"]["llm"]["type"]
        user_id = config["configurable"]["user_id"]
        thread_id = config["configurable"]["thread_id"]

        # 메타데이터 조회
        metadata = load_metadata(thread_id)
        logging.info(f"character_metadata: {metadata}")
        # metadata_val = metadata.values
        # logging.info(f"character_metadata_val: {metadata_val}")

        # 최신 요약 불러오기
        summaries = load_summary(thread_id)
        latest_summary = summaries if summaries else "요약 정보 없음"
        logging.info(f"latest_summary: {latest_summary}")

        chat = load_chat(thread_id)

        # 모델 초기화
        if llm_type == "gemini":
            model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-latest",
                google_api_key=config["configurable"]["llm"]["api_key"]
            )

        # 대화 메시지 구성
        messages = []
        for turn in chat:
            messages.extend([
                HumanMessage(content=turn["U"]),
                AIMessage(content=turn["A"])
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
        logging.info(f"llm response: {response}")
    except Exception as e:
        error_msg = str(e)
        logging.error(f"llm response error: {error_msg}")
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            return {
                "error_code": 429,
                "error_message": "API rate limit exceeded"
            }
        return e

    # 새로운 history 저장
    old_history = load_chat(thread_id)
    new_turn = {"U": state["input_text"], "A": response.content}

    # 기존 history에 새 대화 추가 후 최신 30턴 유지
    new_history = (old_history + [new_turn])[-30:]

    # 이후에 저장
    save_chat(thread_id, new_history)

    output = {
        "output_text": response.content,
        "history": new_history
    }

    logging.info(f"output: {output}")

    return output

def callmodel_branch(state: State, config):
    # 1. 429 에러 체크
    error = ""
    if isinstance(state, Exception):
        error = str(state)
    elif isinstance(state, dict):
        error = state.get("error", "")
    if "429" in error or "ResourceExhausted" in error:
        print("429 에러 감지: 실행 중단")
        return END

    # 2. 5턴마다 요약 여부 판단
    history_len = len(state.get("history", []))
    if history_len != 0 and history_len % 5 == 0:
        return "summarize"

    # 3. 그 외에는 종료
    return END


builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_node("summarize", summarize_history)

# 시작 노드 등록
builder.add_edge(START, "call_model")

# call_model 이후 429 에러 판단 & 요약조건 되는지 판단
builder.add_conditional_edges(
    "call_model",
    callmodel_branch,
    {
        END: END,
        "summarize": "summarize",
    }
)

# summarize → 종료
builder.add_edge("summarize", END)

graph = builder.compile(checkpointer=checkpointer)