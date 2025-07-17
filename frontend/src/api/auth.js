import { apiClient } from "./apiClient.js"
import axios from 'axios';


export const CheckUsername = async (username) => {
    try {
        const checkResponse = await apiClient.get(
            `api/accounts/check-username/?username=${username}`, {
                
            }
        )
        console.log("checkResponse: ", checkResponse)
        return checkResponse
    } catch (e) {
        if (axios.isAxiosError(e)) {
            alert("데이터를 요청하는중 에러가 발생하였습니다.")
            console.log(e)
        } else {
            // 기타 에러 처리
            alert("예상치 못한 오류가 발생했습니다.")
        }
        throw e
    }
}

export const CheckEmail = async (email) => {
    try {
        const checkResponse = await apiClient.get(
            `api/accounts/check-email/?email=${email}`, {
                
            }
        )
        console.log("checkResponse: ", checkResponse)
        return checkResponse
    } catch (e) {
        if (axios.isAxiosError(e)) {
            alert("데이터를 요청하는중 에러가 발생하였습니다.")
            console.log(e)
        } else {
            // 기타 에러 처리
            alert("예상치 못한 오류가 발생했습니다.")
        }
        throw e
    }
}

export const SignUpAPI = async (formData) => {
    try {
        const signupResponse = await apiClient.post(
            `api/accounts/signup/`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            }
        );
        console.log("signupResponse: ", signupResponse)
        alert("회원가입 완료");
        return signupResponse
    }  catch (e) {
        if (axios.isAxiosError(e)) {
            alert("회원가입 데이터를 처리하는중 에러가 발생하였습니다.")
            console.log(e)
        } else {
            // 기타 에러 처리
            alert("예상치 못한 오류가 발생했습니다.")
        }
        throw e
    }
}

export const LoginAPI = async (data) => {
    try {
        const loginResponse = await apiClient.post(
            `api/accounts/login/`,
            JSON.stringify(data),
            {
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        );
        console.log("loginResponse: ", loginResponse)
        const accessToken = loginResponse.data.access;
        const refreshToken = loginResponse.data.refresh;
        sessionStorage.setItem('accessToken', accessToken);
        sessionStorage.setItem('refreshToken', refreshToken);
        alert("로그인 완료");
    }  catch (e) {
        if (axios.isAxiosError(e)) {
            alert("데이터를 처리하는중 에러가 발생하였습니다.")
            console.log(e)
        } else {
            // 기타 에러 처리
            alert("예상치 못한 오류가 발생했습니다.")
        }
        throw e
    }
}

export function getAccessToken() {
    return sessionStorage.getItem('accessToken');
}

export function isAccessTokenValid() {
    const token = getAccessToken();
    if (!token) return false;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Math.floor(Date.now() / 1000);
        return payload.exp > now;
    } catch {
        return false;
    }
}