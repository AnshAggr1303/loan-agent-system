/* eslint-disable @typescript-eslint/no-explicit-any */
// ============================================================================
// GROQ CLIENT - LLM for Master Agent NLU (llama-3.3-70b-versatile)
// ============================================================================

import Groq from 'groq-sdk';

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

export interface GroqChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface GroqChatOptions {
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
}

/**
 * Send chat completion request to Groq API
 */
export async function chatCompletion(
  messages: GroqChatMessage[],
  options: GroqChatOptions = {}
): Promise<string> {
  try {
    const chatCompletion = await groq.chat.completions.create({
      messages,
      model: 'llama-3.3-70b-versatile',
      temperature: options.temperature ?? 0.7,
      max_tokens: options.max_tokens ?? 1024,
      top_p: options.top_p ?? 1,
    });

    return chatCompletion.choices[0]?.message?.content || '';
  } catch (error) {
    console.error('Groq API Error:', error);
    throw new Error('Failed to get response from LLM');
  }
}

/**
 * Extract intent and entities from user message
 */
export async function extractIntent(
  userMessage: string,
  conversationHistory: GroqChatMessage[] = []
): Promise<{
  intent: string;
  entities: Record<string, any>;
  response: string;
}> {
  const systemPrompt = `You are an AI assistant for a loan application chatbot. Your role is to:
1. Understand the user's intent
2. Extract relevant entities (PAN, phone, income, loan amount, etc.)
3. Generate a natural, conversational response

Extract the following information if present:
- pan_number: PAN card number (format: AAAAA1234A)
- phone: 10-digit phone number
- employment_type: Salaried, Self-Employed, or Business Owner
- monthly_income: Monthly income in rupees
- loan_amount: Requested loan amount
- loan_purpose: Purpose of the loan
- preferred_tenure: Loan tenure in months
- existing_emi: Total monthly EMI for existing loans
- company_name: Name of employer

Respond in JSON format:
{
  "intent": "provide_pan" | "provide_phone" | "provide_employment" | "provide_income" | "provide_loan_details" | "provide_emi" | "greeting" | "query" | "other",
  "entities": {
    "pan_number": "...",
    "phone": "...",
    // ... other extracted entities
  },
  "response": "Natural language response to the user"
}`;

  const messages: GroqChatMessage[] = [
    { role: 'system', content: systemPrompt },
    ...conversationHistory,
    { role: 'user', content: userMessage },
  ];

  try {
    const completion = await chatCompletion(messages, {
      temperature: 0.3, // Lower temperature for more consistent extraction
      max_tokens: 512,
    });

    // Parse JSON response
    const jsonMatch = completion.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('Invalid JSON response from LLM');
    }

    const parsed = JSON.parse(jsonMatch[0]);
    return {
      intent: parsed.intent || 'other',
      entities: parsed.entities || {},
      response: parsed.response || 'I understand. Let me help you with that.',
    };
  } catch (error) {
    console.error('Intent extraction error:', error);
    // Fallback response
    return {
      intent: 'other',
      entities: {},
      response: 'I understand. Could you provide more details?',
    };
  }
}

/**
 * Generate natural language response based on context
 */
export async function generateResponse(
  context: string,
  userMessage: string
): Promise<string> {
  const systemPrompt = `You are a friendly loan assistant helping users apply for personal loans. 
Keep responses conversational, warm, and professional. 
Ask one question at a time. Be encouraging and helpful.
Current context: ${context}`;

  const messages: GroqChatMessage[] = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userMessage },
  ];

  return await chatCompletion(messages, {
    temperature: 0.8,
    max_tokens: 256,
  });
}