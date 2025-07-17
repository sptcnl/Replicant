import React, { useState } from 'react';
import { LoginAPI } from './api/auth.js';
import './Modal.css'

function Login({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async e => {
        e.preventDefault();
        setError('');
        await LoginAPI({ username, password });
        if (onLogin) onLogin();
    };

    return (
        <form onSubmit={handleSubmit} style={{ maxWidth: 320, margin: '0 auto', padding: 32, borderRadius: 8 }}>
            <h2 style={{ color: '#e0e0e0' }}>로그인</h2>
            <div style={{ marginBottom: 16 }}>
                <input
                type="text"
                placeholder="아이디"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                style={{ width: '100%', padding: 8 }}
                />
            </div>
            <div style={{ marginBottom: 16 }}>
                <input
                type="password"
                placeholder="비밀번호"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                style={{ width: '100%', padding: 8 }}
                />
            </div>
            {error && <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>}
            <button type="submit" style={{ width: '100%', padding: 10, background: '#999999', color: 'white', border: 'none', borderRadius: 4 }}>로그인</button>
        </form>
    );
};

export default Login;