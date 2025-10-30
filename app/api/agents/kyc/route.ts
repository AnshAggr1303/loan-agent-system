// ============================================================================
// KYC VERIFICATION API ENDPOINT
// Path: loan-agent-system/app/api/agents/kyc/route.ts
// ============================================================================

import { NextRequest, NextResponse } from 'next/server';
import { KYCAgent } from '@/lib/agents/kyc-agent';
import { createClient } from '@/lib/supabase/server';

export const runtime = 'edge';

/**
 * POST /api/agents/kyc
 * Verify PAN and fetch customer KYC details
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

    // Initialize KYC agent
    const kycAgent = new KYCAgent();

    // Verify KYC
    const result = await kycAgent.verify(pan);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          error: result.error,
        },
        { status: 400 }
      );
    }

    // Save KYC verification to database (cache)
    try {
      const supabase = await createClient();
      await supabase.from('kyc_verifications').upsert({
        pan_number: result.data!.pan_number,
        full_name: result.data!.full_name,
        kyc_status: result.data!.kyc_status,
        verified_at: new Date().toISOString(),
      });
    } catch (dbError) {
      console.error('Database error (non-critical):', dbError);
    }

    // Return success response
    return NextResponse.json({
      success: true,
      data: result.data,
      message: kycAgent.generateResponse(result),
    });

  } catch (error) {
    console.error('KYC API Error:', error);
    return NextResponse.json(
      {
        error: 'Failed to verify KYC',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/agents/kyc?pan=XXXXX
 * Get cached KYC verification result
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const pan = searchParams.get('pan');

    if (!pan) {
      return NextResponse.json(
        { error: 'PAN number is required' },
        { status: 400 }
      );
    }

    const supabase = await createClient();
    const { data, error } = await supabase
      .from('kyc_verifications')
      .select('*')
      .eq('pan_number', pan.toUpperCase())
      .single();

    if (error || !data) {
      return NextResponse.json(
        { error: 'KYC record not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data,
    });

  } catch (error) {
    console.error('KYC GET Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch KYC data' },
      { status: 500 }
    );
  }
}