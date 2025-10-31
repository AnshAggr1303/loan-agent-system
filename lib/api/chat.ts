// lib/api/chat.ts

import { ChatRequest, ChatResponse } from '@/types/chat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Chat API error:', error);
    throw error;
  }
}

export async function getSession(sessionId: string) {
  try {
    const response = await fetch(`${API_URL}/api/session/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Session API error:', error);
    throw error;
  }
}