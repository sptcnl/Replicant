import React, { useState } from 'react';
import ChatList from './ChatList';
import Chat from './Chat';
import Login from './Login';
import { isAccessTokenValid, getAccessToken } from './api/auth.js';
import { getChatList } from './api/chat.js';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(isAccessTokenValid());

  // 로그인 성공 시 콜백
  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  // 만약 로그아웃 기능도 추가하고 싶으면
  const handleLogout = () => {
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    setIsLoggedIn(false);
  };

  
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [messages, setMessages] = useState([]);
  
  const handleSelectFriend = async (friend) => {
    setSelectedFriend(friend);
    console.log(`selected friend: ${friend.name}: ${friend.id}`)
    
    try {
      // API 호출 - friend.id가 room_id라고 가정
      const chatList = await getChatList(friend.id);
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
  };
  
  const handleSendMessage = (content) => {
    setMessages([...messages, { id: Date.now(), content, sender_type: 'U' }]);
  };

  return (
    isLoggedIn ? (
      <div className="chat-container">
        <button onClick={handleLogout} style={{ position: 'absolute', top: 10, right: 10 }}>로그아웃</button>
        <ChatList
          selectedId={selectedFriend?.id}
          onSelectFriend={handleSelectFriend}
        />
        <Chat
          friend={selectedFriend}
          messages={messages}
          onSendMessage={handleSendMessage}
        />
      </div>
    ) : (
      <div className="modal-overlay">
        <div className="modal-content">
          <Login onLogin={handleLogin} />
        </div>
      </div>
    )
  );
}

export default App;