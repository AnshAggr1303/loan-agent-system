// ============================================================================
// KYC VERIFICATION AGENT
// Path: loan-agent-system/lib/agents/kyc-agent.ts
// ============================================================================

import { verifyKYC, calculateAge } from '@/lib/mock-data/kyc-database';
import { KYCVerificationResult } from '@/types';
import { isValidPAN } from '@/lib/utils/calculations';

/**
 * KYC Verification Agent
 * Verifies PAN and fetches customer details from mock database
 */
export class KYCAgent {
  /**
   * Verify customer KYC using PAN number
   */
  async verify(pan: string): Promise<KYCVerificationResult> {
    try {
      // Validate PAN format
      if (!isValidPAN(pan)) {
        return {
          success: false,
          error: 'Invalid PAN format. PAN should be like ABCDE1234F',
        };
      }

      // Fetch from mock database
      const record = await verifyKYC(pan);

      if (!record) {
        return {
          success: false,
          error: 'PAN not found in our records. Please verify the PAN number.',
        };
      }

      // Check KYC status
      if (record.kyc_status !== 'VERIFIED') {
        return {
          success: false,
          error: `KYC Status: ${record.kyc_status}. Please complete your KYC verification first.`,
        };
      }

      // Calculate age
      const age = calculateAge(record.date_of_birth);

      return {
        success: true,
        data: {
          pan_number: record.pan_number,
          full_name: record.full_name,
          date_of_birth: record.date_of_birth,
          age,
          phone: record.phone,
          kyc_status: record.kyc_status,
        },
      };
    } catch (error) {
      console.error('KYC Agent Error:', error);
      return {
        success: false,
        error: 'Failed to verify KYC. Please try again.',
      };
    }
  }

  /**
   * Generate natural language response for KYC verification result
   */
  generateResponse(result: KYCVerificationResult): string {
    if (!result.success) {
      return `❌ ${result.error}`;
    }

    const { full_name, age } = result.data!;
    return `✅ KYC Verified successfully!\n\nWelcome, ${full_name}! Your details have been verified. Let's continue with your loan application.`;
  }
}