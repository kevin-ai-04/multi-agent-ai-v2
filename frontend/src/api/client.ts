const API_BASE_URL = "http://localhost:8000";

interface ChatRequest {
    input_text: string;
    agent_a_enabled: boolean;
    agent_b_enabled: boolean;
}

interface ChatResponse {
    response_text: string;
    steps: string[];
}

export interface EmailItem {
    id: string;
    subject: string;
    sender: string;
    date: string;
    body: string;
    folder: string;
}

export interface SendEmailRequest {
    to_email: string;
    subject: string;
    body: string;
}

export async function sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}

export async function fetchEmails(folder: string): Promise<EmailItem[]> {
    const response = await fetch(`${API_BASE_URL}/emails/${folder}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch emails: ${response.statusText}`);
    }
    return response.json();
}

export async function sendEmail(data: SendEmailRequest): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/emails/send`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        throw new Error(`Failed to send email: ${response.statusText}`);
    }
}
