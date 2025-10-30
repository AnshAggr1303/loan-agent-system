// ============================================================================
// DOCUMENT GENERATION API ENDPOINT
// Path: loan-agent-system/app/api/agents/document/route.ts
// ============================================================================

import { NextRequest, NextResponse } from 'next/server';
import { generateSanctionLetter, generateSanctionLetterFilename } from '@/lib/utils/pdf-generator';
import { SanctionLetterData } from '@/types';
import { calculateProcessingFee } from '@/lib/utils/calculations';

export const runtime = 'nodejs'; // PDFKit requires Node.js runtime

/**
 * POST /api/agents/document
 * Generate loan sanction letter PDF
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      applicationId,
      customerName,
      panNumber,
      phone,
      sanctionedAmount,
      interestRate,
      tenure,
      monthlyEmi,
    } = body;

    // Validate required fields
    if (!applicationId || !customerName || !sanctionedAmount || !interestRate || !tenure || !monthlyEmi) {
      return NextResponse.json(
        { error: 'Missing required fields for document generation' },
        { status: 400 }
      );
    }

    // Calculate processing fee
    const processingFee = calculateProcessingFee(sanctionedAmount);

    // Prepare sanction letter data
    const letterData: SanctionLetterData = {
      application_id: applicationId,
      customer_name: customerName,
      pan_number: panNumber || 'N/A',
      phone: phone || 'N/A',
      sanctioned_amount: sanctionedAmount,
      interest_rate: interestRate,
      tenure: tenure,
      monthly_emi: monthlyEmi,
      processing_fee: processingFee,
      date: new Date().toISOString(),
    };

    // Generate PDF
    const pdfBuffer = await generateSanctionLetter(letterData);

    // Convert Node Buffer to Uint8Array for Web/Fetch BodyInit compatibility
    const pdfUint8 = new Uint8Array(pdfBuffer);

    // Generate filename
    const filename = generateSanctionLetterFilename(applicationId, customerName);

    // Return PDF as response
    return new NextResponse(pdfUint8, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Content-Length': String(pdfUint8.byteLength),
      },
    });

  } catch (error) {
    console.error('Document Generation Error:', error);
    return NextResponse.json(
      {
        error: 'Failed to generate sanction letter',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/agents/document/health
 * Health check for document service
 */
export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: 'Document Generation API',
    timestamp: new Date().toISOString(),
    supportedFormats: ['PDF'],
  });
}