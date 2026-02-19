import axios from 'axios';

const API_Base_URL = 'http://localhost:8000';

export interface ChatRequest {
    input_text: string;
    agent_a_enabled: boolean;
    agent_b_enabled: boolean;
}

export interface ChatResponse {
    response_text: string;
    steps: string[];
}

export const sendMessage = async (payload: ChatRequest): Promise<ChatResponse> => {
    try {
        const response = await axios.post<ChatResponse>(`${API_Base_URL}/chat`, payload);
        return response.data;
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
};
