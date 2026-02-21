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
    has_analysis?: boolean;
    priority?: string;
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

export async function syncEmails(folder: string): Promise<{ count: number; message: string }> {
    const response = await fetch(`${API_BASE_URL}/emails/sync?folder=${folder}`, {
        method: "POST",
    });
    if (!response.ok) {
        throw new Error(`Failed to sync emails: ${response.statusText}`);
    }
    return response.json();
}

// --- Database Functionality ---

export async function getTables(): Promise<{ tables: string[] }> {
    const response = await fetch(`${API_BASE_URL}/database/tables`);
    if (!response.ok) {
        throw new Error(`Failed to fetch tables: ${response.statusText}`);
    }
    return response.json();
}

export async function getTableData(tableName: string): Promise<{ data: any[] }> {
    const response = await fetch(`${API_BASE_URL}/database/tables/${tableName}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch table data for ${tableName}: ${response.statusText}`);
    }
    return response.json();
}

export async function updateTableRow(tableName: string, originalRow: any, updatedRow: any): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/database/tables/${tableName}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            original_row: originalRow,
            updated_row: updatedRow
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to update row: ${response.statusText}`);
    }
    return response.json();
}

export async function deleteTableData(tableName: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/database/tables/${tableName}`, {
        method: "DELETE",
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to delete table data: ${response.statusText}`);
    }
    return response.json();
}

// --- Email Analysis API ---

export async function analyzeEmail(emailId: string): Promise<{ status: string, data: any, step?: string }> {
    const response = await fetch(`${API_BASE_URL}/emails/${emailId}/analyze`, {
        method: "POST",
    });
    if (!response.ok) {
        throw new Error(`Failed to analyze email: ${response.statusText}`);
    }
    return response.json();
}

export async function analyzeAllEmails(): Promise<{ status: string, processed_count: number, results: any[] }> {
    const response = await fetch(`${API_BASE_URL}/emails/analyze_all`, {
        method: "POST",
    });
    if (!response.ok) {
        throw new Error(`Failed to analyze all emails: ${response.statusText}`);
    }
    return response.json();
}

export async function getEmailAnalysis(emailId: string): Promise<{ status: string, data?: any }> {
    const response = await fetch(`${API_BASE_URL}/emails/${emailId}/analysis`);
    if (!response.ok) {
        if (response.status === 404) return { status: "not_found" };
        throw new Error(`Failed to fetch email analysis: ${response.statusText}`);
    }
    return response.json();
}
