import React, { useState, useEffect } from 'react';
import ChatList from './ChatList';
import Chat from './Chat';
import { getCharacterList } from './api/character.js';
import defaultProfile from './assets/default.jpg';
import Login from './Login';
import { isAccessTokenValid, getAccessToken } from './api/auth.js';

function App() {
  const [friends, setFriends] = useState([
    { id: "1a", name: '김민수', avatar: defaultProfile, status: 'offline' },
    { id: "2a", name: '이지은', avatar: defaultProfile, status: 'offline' },
    { id: "3a", name: '박준호', avatar: defaultProfile, status: 'offline' },
  ]);
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

  
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const response = await getCharacterList();
        console.log("getCharacterList response: ", response);
        const characters = response.data.map((item, idx) => ({
          id: item.id,
          name: item.name,
          avatar: item.profileImg || defaultProfile, // avatar가 없으면 기본값
          status: 'online',     // status도 기본값 지정
        }));
        
        setFriends(prevFriends => [...prevFriends, ...characters]);
        console.log("characters: ", ...characters);
      } catch (e) {
        // 에러는 getCharacterList에서 처리
      }
    };
    
    fetchCharacters();
  }, []);
  
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [messages, setMessages] = useState([]);
  
  const handleSelectFriend = (friend) => {
    setSelectedFriend(friend);
    // 실제로는 서버에서 해당 친구와의 메시지 가져오기
    setMessages([
      { id: 1, text: '안녕하세요!', sender: friend.id },
      { id: 2, text: '오늘 뭐 할까요?', sender: 'me' },
    ]);
  };
  
  const handleSendMessage = (text) => {
    setMessages([...messages, { id: Date.now(), text, sender: 'me' }]);
  };

  return (
    isLoggedIn ? (
      <div className="chat-container">
        <button onClick={handleLogout} style={{ position: 'absolute', top: 10, right: 10 }}>로그아웃</button>
        <ChatList
          friends={friends}
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