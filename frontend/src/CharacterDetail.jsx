import React from 'react';

function CharacterDetailPopup({ friend }) {
    if (!friend) return null;
    const tags = friend.tags || []
    return (
        <div>
            <div style={{height: 150}}>
                <img src={friend.avatar} alt={friend.name} style={{ width: 90, height: 90, borderRadius: '50%', objectFit: 'cover' }} />
                <h4 style={{ margin: '8px 0 4px 0' }}>{friend.name}</h4>
                <div>상태: {friend.status}</div>
            </div>
            <div>
                <div style={{marginTop: 10}}>
                    {tags.map((tag, idx) => (
                        <span key={idx} style={{ marginRight: 8 }}>#{tag}</span>
                    ))}
                </div>
                <div style={{marginTop: 5}}>{friend.scenario}</div>
            </div>
        </div>
    );
}

export default CharacterDetailPopup;