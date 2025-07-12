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
    const socket = new WebSocket(`ws://localhost:8000/ws/chat/${friend.id}/`);
    ws.current = socket;

    socket.onopen = () => {
      console.log('WebSocket connected');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('data: ', data);
      // 메시지 수신 시 상태 갱신
      const msg = data.message;
      onSendMessage({
        id: msg.id,
        text: msg.content,
        sender: msg.sender_type,
      });
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      socket.close();
    };
  }, [friend, onSendMessage]);

  const handleSend = () => {
    if (inputText.trim() === '' || !ws.current || ws.current.readyState !== 1) return;
    // 메시지 전송
    ws.current.send(JSON.stringify({
      text: inputText,
      sender: 'me',
    }));
    setInputText('');
    // 로컬에서 바로 보이게
    onSendMessage({
      id: Date.now(),
      text: inputText,
      sender: 'me',
    });
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
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`message ${msg.sender === 'me' ? 'me' : 'friend'}`}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <div className="message-input">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="메시지를 입력하세요"
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
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