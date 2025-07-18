import React, { useState, useEffect, useRef } from 'react';

function Chat({ friend, messages, onSendMessage }) {
  const [inputText, setInputText] = useState('');

  const ws = useRef(null);

  // 친구(채팅방) 변경 시 웹소켓 연결/해제
  useEffect(() => {
    if (!friend) return;
    // 기존 연결 종료
    if (ws.current) {
      ws.current.close();
    }
    // 새 연결 생성
    const token = sessionStorage.getItem('accessToken');
    const socket = new WebSocket(`ws://localhost:8000/ws/chat/${friend.id}/?token=${token}`);
    ws.current = socket;

    let pingInterval = null;

    socket.onopen = () => {
      console.log('WebSocket connected');

      pingInterval = setInterval(() => {
        if (ws.current && ws.current.readyState === 1) {
          ws.current.send(JSON.stringify({ type: "ping" }));
        }
      }, 20000);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "pong") return;
        // data.chats가 배열이 아니라 객체라면 그대로 사용
        const msg = data.chats;
        if (msg && typeof msg === 'object' && msg.id && msg.content) {
          console.log(`onmessage 시작`);
          onSendMessage({
            id: msg.id,
            content: msg.content,
            sender_type: msg.sender_type,
          });
          console.log(`onmessage 마무리`);
        }
      } catch (e) {
        console.error('메시지 파싱 에러:', e);
      }
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    socket.onerror = (e) => {
      console.error('WebSocket error:', e);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
        ws.current = null;
        // 타이머 정리
      if (pingInterval) {
        clearInterval(pingInterval);
      }
      }
    };
  }, [friend, onSendMessage]);

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
    // 로컬에서 바로 보이게
    onSendMessage(
      inputText,
    );
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