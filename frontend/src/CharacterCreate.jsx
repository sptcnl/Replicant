import React, { useState, useEffect } from 'react';
import { createCharacter, getTagList } from './api/character.js'
import './Modal.css';


const CharacterCreate = ({ onCreated }) => {
    const [allHashtags, setAllHashtags] = useState([]);
    const [name, setName] = useState('');
    const [profileImage, setProfileImage] = useState(null);
    const [status, setStatus] = useState('online');
    const [scenario, setScenario] = useState('');
    const [preview, setPreview] = useState(null);
    const [hashtagInput, setHashtagInput] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);

    // 해시태그 검색 결과
    const filteredTags = allHashtags.filter(
        tag => tag.includes(hashtagInput) && !selectedTags.includes(tag)
    );

    useEffect(() => {
    const fetchTags = async () => {
        try {
            const response = await getTagList();
            console.log('tagListResponse:', response);
            // API 응답이 배열이라면 그대로, 객체라면 response.data로 접근
            setAllHashtags(response.data); 
        } catch (error) {
        }
    };
        fetchTags();
    }, []);

    // 해시태그 추가
    const addTag = tag => setSelectedTags([...selectedTags, tag]);
    // 해시태그 제거
    const removeTag = tag => setSelectedTags(selectedTags.filter(t => t !== tag));

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        setProfileImage(file);
        if (file) {
        setPreview(URL.createObjectURL(file));
        } else {
        setPreview(null);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append('name', name);
        formData.append('profileImg', profileImage);
        formData.append('scenario', scenario);
        selectedTags.forEach(tag => {
            formData.append('writeTag', tag);
        });

        try {
            const response = await createCharacter(formData);
            console.log("getCharacterCreate response: ", response);
        } catch (error) {
            alert('캐릭터 생성 실패: ' + (error.response?.data?.message || error.message));
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="preview">
                {preview && <img src={preview} alt="미리보기" width={300} height={300} style={{ objectFit: 'cover', borderRadius: '50%', marginBottom: 15 }} />}
            </div>
            <div>
                <div className="form-row">
                    <label>이름: </label>
                    <input
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    required
                    />
                </div>
                <div className="form-row">
                    <label>프로필 이미지: </label>
                    <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    />
                </div>
                <div className="form-row">
                    <label>시나리오: </label>
                    <textarea value={scenario} onChange={e => setScenario(e.target.value)} style={{ flex: 1 }}/>
                </div>
                <div className="form-row">
                    <label>캐릭터 태그: </label>
                    <div style={{ flex: 1 }}>
                        <input
                        type="text"
                        placeholder="캐릭터 태그 검색"
                        value={hashtagInput}
                        onChange={e => setHashtagInput(e.target.value)}
                        style={{ width: '70%', marginBottom: 5 }}
                        onKeyDown={e => {
                            if (e.key === "Enter") {
                            e.preventDefault();
                            // 입력값이 비어있지 않고, 이미 선택된 태그가 아니라면 추가
                            if (hashtagInput.trim() && !selectedTags.includes(hashtagInput.trim())) {
                                addTag(hashtagInput.trim());
                            }
                            }
                        }}
                        />
                        <div className="hashtag-search-list">
                        {hashtagInput && filteredTags.map(tag => (
                            <span key={tag} className="hashtag-suggestion" onClick={() => addTag(tag)}>
                            {tag}
                            </span>
                        ))}
                        </div>
                        <div className="hashtag-selected-list" style={{ marginTop: 8 }}>
                        {selectedTags.map(tag => (
                            <span key={tag} className="hashtag-selected">
                            {tag}
                            <button className="cancel-btn" type="button" onClick={() => removeTag(tag)} style={{ marginLeft: 4, background: 'none' }}>×</button>
                            </span>
                        ))}
                        </div>
                    </div>
                </div>
                <button type="submit">캐릭터 생성</button>
            </div>
        </form>
    );
};

export default CharacterCreate;