// ============================================================================
// MAIN CHAT API ENDPOINT
// Path: loan-agent-system/app/api/chat/route.ts
// ============================================================================

import { NextRequest, NextResponse } from 'next/server';
import { Orchestrator } from '@/lib/agents/orchestrator';
import { ConversationState } from '@/types';
import { createClient } from '@/lib/supabase/server';

export const runtime = 'edge';

/**
 * POST /api/chat
 * Main chat endpoint that processes user messages
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversationState } = body;

    // Validate input
    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    if (!conversationState) {
      return NextResponse.json(
        { error: 'Conversation state is required' },
        { status: 400 }
      );
    }

    // Initialize orchestrator
    const orchestrator = new Orchestrator();

    // Process the message
    const result = await orchestrator.process({
      user_message: message,
      conversation_state: conversationState as ConversationState,
    });

    // Save conversation to database (optional)
    try {
      const supabase = await createClient();
      const { data: { user } } = await supabase.auth.getUser();

      if (user && conversationState.application_id) {
        // Save user message
        await supabase.from('conversation_logs').insert({
          application_id: conversationState.application_id,
          sender: 'user',
          message: message,
        });

        // Save agent response
        await supabase.from('conversation_logs').insert({
          application_id: conversationState.application_id,
          sender: 'agent',
          message: result.response,
          metadata: {
            agent_type: result.agent_used,
          },
        });
      }
    } catch (dbError) {
      console.error('Database error (non-critical):', dbError);
      // Don't fail the request if DB save fails
    }

    // Return response
    return NextResponse.json({
      success: true,
      response: result.response,
      updated_state: result.updated_state,
      agent_used: result.agent_used,
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    return NextResponse.json(
      {
        error: 'Failed to process message',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/chat
 * Health check endpoint
 */
export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    message: 'Chat API is running',
    timestamp: new Date().toISOString(),
  });
}