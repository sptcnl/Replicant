import React, { useState } from 'react';

function Chat({ friend, messages, onSendMessage }) {
  const [inputText, setInputText] = useState('');

  const handleSend = () => {
    if (inputText.trim() === '') return;
    onSendMessage(inputText);
    setInputText('');
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