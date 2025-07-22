import React, { useState, useEffect, useRef } from 'react';
import { getChatList } from './api/chat.js';
import { jwtDecode } from "jwt-decode";
import { v5 as uuidv5 } from 'uuid';

function Chat({ friend }) {
  const MY_NAMESPACE = uuidv5.DNS;
  const token = sessionStorage.getItem('accessToken');
  let userId;

  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([]);

  const ws = useRef(null);
  const reconnectTimer = useRef(null);
  const pingInterval = useRef(null);
  const shouldReconnect = useRef(true);

  const handleFriendMessages = async (friend) => {
    if (token) {
          const decoded = jwtDecode(token);
          console.log(decoded);
          // decoded.user_id, decoded.id, decoded.username 등 실제 백엔드 JWT에 들어있는 값 key명에 맞게
          userId = decoded.user_id || decoded.id;
        }
    
        
        try {
          // API 호출 - friend.id가 room_id라고 가정
          const roomId = uuidv5(friend.id + userId, MY_NAMESPACE);
          const chatList = await getChatList(roomId);
          console.log(`chatList: ${typeof(chatList)}, ${chatList}`)
          const chatData = Array.isArray(chatList) ? chatList : chatList.data || [];
          const normalizedChatList = chatData.map(msg => ({
            id: msg.id,
            content: msg.content,
            sender_type: msg.senderType,
            created_at: msg.createdAt,
            room: msg.room,
        }));
        
          setMessages(normalizedChatList);
        } catch (e) {
          console.error('메시지 불러오기 실패:', e);
          setMessages([]); // 실패하면 메시지 초기화
        }
  }

  // 친구(채팅방) 변경 시 웹소켓 연결/해제
  useEffect(() => {
    if (!friend) return;
    // 기존 연결 종료
    if (ws.current) {
      ws.current.close(1000, "정상적인 friend 값이 바뀔때 연결종료");
      console.log('[타이밍 체크용] 웹소켓 초기 연결 종료');
    }
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
    }
    if (pingInterval.current) {
      clearInterval(pingInterval.current);
    }

    // 새 연결 생성
    const connectWebSocket = () => {
      const token = sessionStorage.getItem("accessToken");
      const socket = new WebSocket(
        `ws://localhost:8000/ws/chat/${friend.id}/?token=${token}`
      );
    
      ws.current = socket;


      socket.onopen = () => {
        console.log('WebSocket connected');

        pingInterval.current = setInterval(() => {
          if (ws.current && ws.current.readyState === 1) {
            ws.current.send(JSON.stringify({ type: "ping" }));
          }
        }, 20000);
      };

      socket.onmessage = (event) => {
        try {
          console.log(`onmessage 들어옴`);
          const data = JSON.parse(event.data);
          if (data.type === "pong") return;

          // data.chats가 배열이 아니라 객체라면 그대로 사용
          if (data.type === "chat_message") {
            console.log(`onmessage res_data: ${data}`)
            const msg = data.message;
            console.log(`onmessage msg: ${msg}`);
            console.log(`onmessage msg type: ${typeof msg}`);
            console.log(`onmessage msg id: ${msg.id}`);
            console.log(`onmessage msg content: ${msg.content}`);
            console.log(`onmessage msg sender_type: ${msg.sender_type}`);
            if (msg && msg.id && msg.content) {
              console.log(`onmessage 시작`);
              console.log(`ai message setMessages하기 이전: ${messages}`)
              setMessages([...messages, {
                id: msg.id,
                content: msg.content,
                sender_type: msg.sender_type,
              }]);
              console.log(`onmessage 마무리`);
            }
          } else {
            console.log(`알수없는 메세지: ${data}`);
          }
        } catch (e) {
          console.error(`메시지 파싱 에러: ${e}`);
        }
      };

      socket.onclose = () => {
        console.log('WebSocket disconnected');

        // 핑 타이머 클리어
        if (pingInterval.current) clearInterval(pingInterval);

        // 재연결 처리
        if (shouldReconnect.current) {
          console.log("🔁 재연결 시도 중...");
          reconnectTimer.current = setTimeout(() => {
            connectWebSocket();
          }, 3000); // 3초 후 재연결
        }
      };

      socket.onerror = (e) => {
        console.error('WebSocket error:', e);
      };
    };

    // 최초 연결 시도
    connectWebSocket();
    handleFriendMessages(friend);

    return () => {
      console.log("🧹 cleanup 시작");
      shouldReconnect.current = false;

      if (ws.current) {
        ws.current.close(1000, "정상적인 말기 연결종료");
        console.log("[타이밍 체크용] 웹소켓 말기 연결 종료");
        // ws.current = null;
      }

      if (pingInterval.current) {
        clearInterval(pingInterval.current);
      }

      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
    };
  }, [friend]);

  const handleSend = () => {
    if (
      inputText.trim() === '' ||
      !ws.current ||
      ws.current.readyState !== WebSocket.OPEN
    )
      return;
    ws.current.send(
      JSON.stringify({
        content: inputText,
        sender_type: 'U',
      })
    );
    setInputText('');
    setMessages([...messages, { id: Date.now(), content: inputText, sender_type: 'U' }]);
  };

  return (
    <div className="chat-area">
      {friend ? (
        <>
          <div className="chat-header">
            <img src={friend.avatar} alt={friend.name} />
            <div className="header-text">
              <div>{friend.name}</div>
              <div>{friend.status}</div>
            </div>
          </div>
          <div className="messages">
            {Array.isArray(messages) &&
              messages.map((msg) => {
                return (
                  <div
                    key={msg.id}
                    className={`message ${msg.sender_type === 'U' ? 'U' : 'A'}`}
                  >
                    {msg.content}
                  </div>
                );
              })}
          </div>
          <div className="message-input">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="메시지를 입력하세요"
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend}>보내기</button>
          </div>
        </>
      ) : (
        <div className="no-chat">친구를 선택해주세요</div>
      )}
    </div>
  );
}

export default Chat;