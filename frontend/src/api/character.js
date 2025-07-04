import { apiClient } from "./apiClient.js"
import axios from 'axios';


export const getCharacterList = async () => {
    try {
        const characterResponse = await apiClient.get(
            `api/characters/`, {
                
            }
        )
        console.log("characterResponse: ", characterResponse)
        return characterResponse
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

export const createCharacter = async () => {
    try {
        const characterResponse = await apiClient.post(
            `api/characters/`, {
                
            }
        )
        console.log("characterResponse: ", characterResponse)
        alert("캐릭터 생성 완료")
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