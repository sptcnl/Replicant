import React, { useState } from "react";
import { CheckUsername, CheckEmail, SignUpAPI } from "./api/auth.js";

function SignUp({ onClose, onSignUpSuccess }) {
    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        gender: "",
        profile_img: null,
        profile_img_preview: null,
    });

    const [checks, setChecks] = useState({
        usernameAvailable: null, // true/false/null
        emailAvailable: null,
    });

    const [errors, setErrors] = useState({});

    // 폼 변경 핸들러
    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((f) => ({ ...f, [name]: value }));

        // 중복 체크 초기화
        if (name === "username") setChecks((c) => ({ ...c, usernameAvailable: null }));
        if (name === "email") setChecks((c) => ({ ...c, emailAvailable: null }));

        // 오류 초기화
        setErrors((err) => ({ ...err, [name]: undefined }));
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        setForm((prev) => ({
            ...prev,
            profile_img: file || null,
        }));

        // 미리보기 생성
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
            setForm((prev) => ({
                ...prev,
                profile_img_preview: reader.result,
            }));
            };
            reader.readAsDataURL(file);
        } else {
            setForm((prev) => ({
            ...prev,
            profile_img_preview: null,
            }));
        }
    };

    // 필수값 검사
    const validateRequired = () => {
        let isValid = true;
        const newErrors = {};

        if (!form.username.trim()) {
        newErrors.username = "사용자 이름을 입력해주세요.";
        isValid = false;
        }

        if (!form.email.trim()) {
        newErrors.email = "이메일을 입력해주세요.";
        isValid = false;
        } else if (!/\S+@\S+\.\S+/.test(form.email)) {
        newErrors.email = "유효한 이메일 주소를 입력해주세요.";
        isValid = false;
        }

        if (!form.password) {
        newErrors.password = "비밀번호를 입력해주세요.";
        isValid = false;
        } else if (form.password.length < 6) {
        newErrors.password = "비밀번호는 6자 이상이어야 합니다.";
        isValid = false;
        }

        setErrors(newErrors);
        return isValid;
    };

    const checkUsernameDuplication = async () => {
        if (!form.username.trim()) {
            setErrors((e) => ({ ...e, username: "먼저 사용자 이름을 입력하세요." }));
            return;
        }

        try {
            const response = await CheckUsername(form.username);
            // response 예: { available: true }
            const available = response.data.available;
            console.log('중복확인 응답:', available);

            setChecks((c) => ({ ...c, usernameAvailable: available }));
            if (!available) {
            setErrors((e) => ({ ...e, username: "" }));
            } else {
            setErrors((e) => ({ ...e, username: undefined }));
            }
        } catch (error) {
            setErrors((e) => ({ ...e, username: "중복확인 도중 오류가 발생했습니다." }));
        }
    };

    const checkEmailDuplication = async () => {
        if (!form.email.trim()) {
            setErrors((e) => ({ ...e, email: "먼저 이메일을 입력하세요." }));
            return;
        }

        try {
            const response = await CheckEmail(form.email);
            // response 예: { available: true }
            const available = response.data.available;
            console.log('중복확인 응답:', available);

            setChecks((c) => ({ ...c, emailAvailable: available }));
            if (!available) {
            setErrors((e) => ({ ...e, email: "" }));
            } else {
            setErrors((e) => ({ ...e, email: undefined }));
            }
        } catch (error) {
            setErrors((e) => ({ ...e, email: "중복확인 도중 오류가 발생했습니다." }));
        }
    };

    // 회원가입 제출
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateRequired()) return;

        if (checks.usernameAvailable === false || checks.emailAvailable === false) {
            alert("중복확인을 통과한 사용자 이름과 이메일을 사용해주세요.");
            return;
        }

        try {
            // 파일 포함 여부에 따라 FormData 생성
            const formData = new FormData();
                formData.append("username", form.username);
                formData.append("email", form.email);
                formData.append("password", form.password);
            if (form.gender) {
                formData.append("gender", form.gender);
            }
            if (form.profile_img) {
                formData.append("profile_img", form.profile_img);
            }

            const obj = {};
            for (const [key, value] of formData.entries()) {
            obj[key] = value;
            }
            console.log(obj);

            // 회원가입 API 호출 (프로필이미지 업로드 지원)
            const response = await SignUpAPI(formData);

            // 성공 시 콜백
            if (onSignUpSuccess) {
                console.log(`onSignUpSuccess: ${onSignUpSuccess}`)
                console.log(`response.data: ${response.data}`)
                onSignUpSuccess(response.data); // 서버의 응답 데이터를 넘겨줌
            }
        } catch (error) {
            // 에러 처리: 서버 오류, 유효성 오류 등
            console.log(`error: ${error}`)
            alert(
                error?.response?.data?.detail ||
                "회원가입 이후 문제가 발생했습니다."
            );
        }
    };


    return (
        <div className="modal-content" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={onClose} aria-label="닫기">
            &times;
            </button>
            <h2>회원가입</h2>
            <form onSubmit={handleSubmit} noValidate>
                {/* username */}
                <div style={{ marginBottom: 12 }}>
                    <label htmlFor="username">
                    사용자 이름 <span style={{ color: "red" }}>*</span>
                    </label>
                    <div style={{ display: "flex", gap: 6 }}>
                    <input
                        id="username"
                        name="username"
                        type="text"
                        value={form.username}
                        onChange={handleChange}
                        aria-describedby="username-error"
                        style={{ flex: 1 }}
                        required
                    />
                    <button type="button" onClick={checkUsernameDuplication} style={{ flexShrink: 0 }}>
                        중복확인
                    </button>
                    </div>
                    {errors.username && (
                    <small id="username-error" style={{ color: "tomato" }}>
                        {errors.username}
                    </small>
                    )}
                    {checks.usernameAvailable === true && (
                    <small style={{ color: "limegreen" }}>사용 가능한 사용자 이름입니다.</small>
                    )}
                    {checks.usernameAvailable === false && (
                    <small style={{ color: "tomato" }}>이미 사용 중인 사용자 이름입니다.</small>
                    )}
                </div>

                {/* email */}
                <div style={{ marginBottom: 12 }}>
                    <label htmlFor="email">
                    이메일 <span style={{ color: "red" }}>*</span>
                    </label>
                    <div style={{ display: "flex", gap: 6 }}>
                    <input
                        id="email"
                        name="email"
                        type="email"
                        value={form.email}
                        onChange={handleChange}
                        aria-describedby="email-error"
                        style={{ flex: 1 }}
                        required
                    />
                    <button type="button" onClick={checkEmailDuplication} style={{ flexShrink: 0 }}>
                        중복확인
                    </button>
                    </div>
                    {errors.email && (
                    <small id="email-error" style={{ color: "tomato" }}>
                        {errors.email}
                    </small>
                    )}
                    {checks.emailAvailable === true && (
                    <small style={{ color: "limegreen" }}>사용 가능한 이메일입니다.</small>
                    )}
                    {checks.emailAvailable === false && (
                    <small style={{ color: "tomato" }}>이미 가입된 이메일입니다.</small>
                    )}
                </div>

                {/* password */}
                <div style={{ marginBottom: 12 }}>
                    <label htmlFor="password">
                    비밀번호 <span style={{ color: "red" }}>*</span>
                    </label>
                    <input
                    id="password"
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleChange}
                    aria-describedby="password-error"
                    required
                    />
                    {errors.password && (
                    <small id="password-error" style={{ color: "tomato" }}>
                        {errors.password}
                    </small>
                    )}
                </div>

                {/* profile_img */}
                <div style={{ marginBottom: 12 }}>
                    <label htmlFor="profile_img">프로필 이미지 (선택)</label>
                    <input
                    id="profile_img"
                    name="profile_img"
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    />
                    {form.profile_img_preview && (
                        <div style={{ marginTop: 6 }}>
                            <img
                            src={form.profile_img_preview}
                            alt="미리보기"
                            style={{ maxWidth: 120, maxHeight: 120, borderRadius: 8 }}
                            />
                        </div>
                    )}
                </div>

                {/* gender */}
                <div style={{ marginBottom: 12 }}>
                    <label htmlFor="gender">성별 (선택)</label>
                    <select id="gender" name="gender" value={form.gender} onChange={handleChange}>
                    <option value="">선택하세요</option>
                    <option value="M">남성</option>
                    <option value="W">여성</option>
                    <option value="O">기타</option>
                    </select>
                </div>

                <button type="submit" style={{ marginTop: 12, width: "100%" }}>
                    회원가입
                </button>
            </form>
        </div>
    );
}

export default SignUp;