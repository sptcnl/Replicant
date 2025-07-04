import React, { useState, useEffect } from 'react';
import ChatList from './ChatList';
import Chat from './Chat';
import {getCharacterList} from './api/character.js';

function App() {
  const [friends, setFriends] = useState([
    { id: 1, name: '김민수', avatar: 'avatar1.png', status: 'online' },
    { id: 2, name: '이지은', avatar: 'avatar2.png', status: 'offline' },
    { id: 3, name: '박준호', avatar: 'avatar3.png', status: 'online' },
  ]);

  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const characters = await getCharacterList();
        setFriends(prevFriends => [...prevFriends, ...characters]);
        console.log("characters: ", ...characters)
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
    <div className="chat-container">
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
  );
}

export default App;