// types/chat.ts

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  conversation_history?: ConversationMessage[];
}

export interface ConversationMessage {
  role: string;
  content: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  session_id: string;
  tools_used: string[];
  response_time_ms: number;
}

export interface Customer {
  id: string;
  user_id: string;
  pan_number: string | null;
  full_name: string;
  email: string;
  phone: string | null;
  employment_type: string | null;
  monthly_income: number | null;
  kyc_status: string;
  created_at: string;
}