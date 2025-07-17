import React, { useState } from 'react';
import { v5 as uuidv5 } from 'uuid';
import { jwtDecode } from "jwt-decode";
import ChatList from './ChatList';
import Chat from './Chat';
import Login from './Login';
import SignUp from './SignUp';
import { isAccessTokenValid, getAccessToken } from './api/auth.js';
import { getChatList } from './api/chat.js';
import './Modal.css'


function App() {
  const MY_NAMESPACE = uuidv5.DNS;
  const [showSignUp, setShowSignUp] = useState(false);
  const token = sessionStorage.getItem('accessToken');
  let userId;

  const openSignUp = () => setShowSignUp(true);
  const closeSignUp = () => setShowSignUp(false);

  const handleSignUpSuccess = (userData) => {
    console.log('회원가입 성공:', userData);
    setShowSignUp(false);
    // 추가 처리 (로그인, 환영 메시지 등)
  };

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

    console.log(token);
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
      <>
        <div>
          <div className="modal-overlay" style={{ zIndex: 1000 }}>
            <div className="modal-content" style={{ zIndex: 1001 }}>
              <Login onLogin={handleLogin} />
              <a className='signup-button' onClick={(e) => { e.preventDefault(); openSignUp(); }} href="#">회원가입</a>
            </div>
          </div>
        </div>

        {/* SignUp 모달은 로그인 모달과 별개로 최상위에 렌더 */}
        {showSignUp && (
          <div className="modal-overlay" onClick={closeSignUp}>
            <div
              className="modal-content"
              role="dialog"
              aria-modal="true"
              onClick={(e) => e.stopPropagation()} // 모달내부 클릭은 바깥 클릭 차단
            >
              <SignUp onClose={closeSignUp} onSignUpSuccess={handleSignUpSuccess} />
            </div>
          </div>
        )}
      </>
    )
  );
}

export default App;