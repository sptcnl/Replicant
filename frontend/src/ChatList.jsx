import React from 'react';

function ChatList({ friends, selectedId, onSelectFriend }) {
  return (
    <div className="friend-list">
      <div className="search-bar">
        <input type="text" placeholder="친구 검색" />
        <button>+</button>
      </div>
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