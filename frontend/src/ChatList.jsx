import React, { useState } from 'react';
import CharacterCreate from './CharacterCreate.jsx';
import './form.css'
import './App.css'

function ChatList({ friends, selectedId, onSelectFriend, onCreated }) {
  const [showCreate, setShowCreate] = useState(false);

  const handleCreateClick = () => setShowCreate(true);
  const handleClose = () => setShowCreate(false);

  const handleCreated = (newCharacter) => {
    setShowCreate(false);
    if (onCreated) onCreated(newCharacter);
  };

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
            <button className="modal-close" style={{color: "#e0e0e0"}} onClick={handleClose}>X</button>
          </div>
        </div>
      )}

      <div className="friend-items">
        {friends.map((friend) => (
          <div
            key={friend.id}
            className={`friend-item ${selectedId === friend.id ? 'selected' : ''}`}
            onClick={() => onSelectFriend(friend)}
          >
            <img src={friend.avatar} alt={friend.name} />
            <div>
              <div className="friend-name">{friend.name}</div>
              <div className="friend-status">{friend.status}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChatList;