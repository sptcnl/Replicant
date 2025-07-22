import React, { useState, useEffect } from 'react';
import CharacterCreate from './CharacterCreate.jsx';
import CharacterDetailPopup from './CharacterDetail.jsx';
import { getCharacterList } from './api/character.js';
import defaultProfile from './assets/default.jpg';
import './App.css'

function ChatList({ selectedId, onSelectFriend, onCreated }) {
  const [friends, setFriends] = useState([
    { id: "1a", name: '김민수', avatar: defaultProfile, status: 'offline', tags: ['바보', '멍청이'], scenario: '' },
    { id: "2a", name: '이지은', avatar: defaultProfile, status: 'offline', tags: [], scenario: '' },
    { id: "3a", name: '박준호', avatar: defaultProfile, status: 'offline', tags: [], scenario: '' },
  ]);
  const [showCreate, setShowCreate] = useState(false);

  const handleCreateClick = () => setShowCreate(true);
  const handleClose = () => setShowCreate(false);

  const [hoveredId, setHoveredId] = useState(null);
  const hoveredFriend = friends.find(friend => friend.id === hoveredId);

  const handleCreated = (newCharacter) => {
    setShowCreate(false);
    // 새 캐릭터를 friends 배열에 추가
    setFriends(prevFriends => [
      ...prevFriends,
      {
        id: newCharacter.id,
        name: newCharacter.name,
        avatar: newCharacter.profileImg || defaultProfile,
        status: 'online',
      }
    ]);
    if (onCreated) onCreated(newCharacter);
  };

  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const response = await getCharacterList();
        console.log("getCharacterList response: ", response);
        const characters = response.data.map((item) => ({
          id: item.id,
          name: item.name,
          avatar: item.profileImg || defaultProfile, // avatar가 없으면 기본값
          status: 'online',     // status도 기본값 지정
          tags: item.readTag,
          scenario: item.scenario
        }));
        
        setFriends(prevFriends => [...prevFriends, ...characters]);
        console.log("characters: ", ...characters);
      } catch (e) {
        // 에러는 getCharacterList에서 처리
      }
    };
    
    fetchCharacters();
  }, []);

  return (
    <div className="friend-list">
      <div className="search-bar">
        <input type="text" placeholder="친구 검색" />
        <button onClick={handleCreateClick}>+</button>
      </div>

      {/* 캐릭터 생성 폼 토글 */}
      {showCreate && (
        <div className="modal-overlay">
          <div className="modal-content">
            <CharacterCreate onCreated={handleCreated} />
            <button className="modal-close" style={{color: "#e0e0e0"}} onClick={handleClose}>&times;</button>
          </div>
        </div>
      )}

      <div className="friend-items">
        {friends.map((friend) => (
          <div
            key={friend.id}
            className={`friend-item ${selectedId === friend.id ? 'selected' : ''}`}
            onClick={() => onSelectFriend(friend)}
            onMouseEnter={() => setHoveredId(friend.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            <img src={friend.avatar || defaultProfile} alt={friend.name} />
            <div>
              <div className="friend-name">{friend.name}</div>
              <div className="friend-status">{friend.status}</div>
            </div>
          </div>
        ))}
      </div>
      <CharacterDetailPopup friend={hoveredFriend} />
    </div>
  );
}

export default ChatList;