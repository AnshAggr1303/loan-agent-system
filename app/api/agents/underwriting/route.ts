// ============================================================================
// UNDERWRITING API ENDPOINT
// Path: loan-agent-system/app/api/agents/underwriting/route.ts
// ============================================================================

import { NextRequest, NextResponse } from 'next/server';
import { UnderwritingAgent } from '@/lib/agents/underwriting-agent';
import { LoanApplicationData } from '@/types';
import { createClient } from '@/lib/supabase/server';
import { v4 as uuidv4 } from 'uuid';

export const runtime = 'edge';

/**
 * POST /api/agents/underwriting
 * Evaluate loan application and make approval decision
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { loanData, userId } = body;

    // Validate input
    if (!loanData || typeof loanData !== 'object') {
      return NextResponse.json(
        { error: 'Loan data is required' },
        { status: 400 }
      );
    }

    // Initialize underwriting agent
    const underwritingAgent = new UnderwritingAgent();

    // Evaluate loan application
    const decision = underwritingAgent.evaluate(loanData as LoanApplicationData);

    // Generate response message
    const responseMessage = underwritingAgent.generateResponse(
      decision,
      loanData.full_name || 'Customer'
    );

    // Save to database if user is authenticated
    let applicationId: string | null = null;

    if (userId) {
      try {
        const supabase = await createClient();
        
        // Create or update loan application
        const applicationData = {
          id: uuidv4(),
          user_id: userId,
          pan_number: loanData.pan_number,
          full_name: loanData.full_name,
          age: loanData.age,
          phone: loanData.phone,
          employment_type: loanData.employment_type,
          monthly_income: loanData.monthly_income,
          company_name: loanData.company_name,
          loan_amount_requested: loanData.loan_amount_requested,
          loan_purpose: loanData.loan_purpose,
          preferred_tenure: loanData.preferred_tenure,
          existing_emi: loanData.existing_emi || 0,
          has_credit_card: loanData.has_credit_card || false,
          credit_card_outstanding: loanData.credit_card_outstanding || 0,
          credit_score: loanData.credit_score,
          credit_status: loanData.credit_status,
          active_loans: loanData.active_loans || 0,
          approval_status: decision.approved ? 'approved' : 'rejected',
          sanctioned_amount: decision.sanctioned_amount,
          interest_rate: decision.interest_rate,
          monthly_emi: decision.monthly_emi,
          rejection_reason: decision.rejection_reason,
          failed_rules: decision.failed_rules,
        };

        const { data, error } = await supabase
          .from('loan_applications')
          .insert(applicationData)
          .select()
          .single();

        if (error) {
          console.error('Database insert error:', error);
        } else {
          applicationId = data.id;
        }
      } catch (dbError) {
        console.error('Database error (non-critical):', dbError);
      }
    }

    // Calculate counter offer for rejected applications
    let counterOffer = null;
    if (!decision.approved) {
      const counterOfferAmount = underwritingAgent.calculateCounterOffer(
        loanData as LoanApplicationData
      );
      if (counterOfferAmount) {
        counterOffer = {
          amount: counterOfferAmount,
          message: `We can offer up to ₹${counterOfferAmount.toLocaleString('en-IN')} instead.`,
        };
      }
    }

    // Return response
    return NextResponse.json({
      success: true,
      decision: decision.approved ? 'approved' : 'rejected',
      data: decision,
      message: responseMessage,
      applicationId,
      counterOffer,
    });

  } catch (error) {
    console.error('Underwriting API Error:', error);
    return NextResponse.json(
      {
        error: 'Failed to evaluate loan application',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/agents/underwriting/application/:id
 * Get loan application details
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const applicationId = searchParams.get('id');

    if (!applicationId) {
      return NextResponse.json(
        { error: 'Application ID is required' },
        { status: 400 }
      );
    }

    const supabase = await createClient();
    const { data, error } = await supabase
      .from('loan_applications')
      .select('*')
      .eq('id', applicationId)
      .single();

    if (error || !data) {
      return NextResponse.json(
        { error: 'Application not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data,
    });

  } catch (error) {
    console.error('Get Application Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch application' },
      { status: 500 }
    );
  }
}