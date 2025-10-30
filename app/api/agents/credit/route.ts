// ============================================================================
// CREDIT CHECK API ENDPOINT
// Path: loan-agent-system/app/api/agents/credit/route.ts
// ============================================================================

import { NextRequest, NextResponse } from 'next/server';
import { CreditAgent } from '@/lib/agents/credit-agent';

export const runtime = 'edge';

/**
 * POST /api/agents/credit
 * Fetch credit score and credit history
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { pan } = body;

    // Validate input
    if (!pan || typeof pan !== 'string') {
      return NextResponse.json(
        { error: 'PAN number is required' },
        { status: 400 }
      );
    }

    // Initialize credit agent
    const creditAgent = new CreditAgent();

    // Check credit
    const result = await creditAgent.checkCredit(pan);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          error: result.error,
        },
        { status: 400 }
      );
    }

    // Check if meets minimum requirement
    const meetsMinimum = creditAgent.meetsMinimumRequirement(result.data!.score);

    // Return success response
    return NextResponse.json({
      success: true,
      data: result.data,
      message: creditAgent.generateResponse(result),
      meetsMinimumRequirement: meetsMinimum,
    });

  } catch (error) {
    console.error('Credit API Error:', error);
    return NextResponse.json(
      {
        error: 'Failed to check credit score',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/agents/credit/health
 * Health check for credit service
 */
export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: 'Credit Assessment API',
    timestamp: new Date().toISOString(),
  });
}