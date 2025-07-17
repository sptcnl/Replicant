import { apiClient } from "./apiClient.js"
import axios from 'axios';

export const getChatList = async (room_id) => {
    try {
        const accessToken = sessionStorage.getItem('accessToken');
        const chatResponse = await apiClient.get(
            `api/chat/${room_id}/`,
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            }
        );
        console.log("chatResponse: ", chatResponse);
        return chatResponse
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