// ============================================================================
// CREDIT ASSESSMENT AGENT
// Path: loan-agent-system/lib/agents/credit-agent.ts
// ============================================================================

import { fetchCreditScore, getCreditScoreBand, calculateRiskLevel } from '@/lib/mock-data/credit-database';
import { CreditCheckResult } from '@/types';

/**
 * Credit Assessment Agent
 * Fetches credit score and analyzes creditworthiness
 */
export class CreditAgent {
  /**
   * Fetch and analyze credit score using PAN
   */
  async checkCredit(pan: string): Promise<CreditCheckResult> {
    try {
      // Fetch from mock credit bureau
      const creditRecord = await fetchCreditScore(pan);

      if (!creditRecord) {
        return {
          success: false,
          error: 'No credit history found. Unable to assess creditworthiness.',
        };
      }

      // Calculate risk level
      const riskLevel = calculateRiskLevel(creditRecord);
      const scoreBand = getCreditScoreBand(creditRecord.score);

      return {
        success: true,
        data: {
          score: creditRecord.score,
          status: creditRecord.status,
          active_loans: creditRecord.active_loans,
          credit_history_years: creditRecord.credit_history_years,
          defaults: creditRecord.defaults > 0 
            ? `${creditRecord.defaults} default(s) in past 2 years` 
            : 'No defaults',
        },
      };
    } catch (error) {
      console.error('Credit Agent Error:', error);
      return {
        success: false,
        error: 'Failed to fetch credit score. Please try again.',
      };
    }
  }

  /**
   * Generate natural language response for credit check result
   */
  generateResponse(result: CreditCheckResult): string {
    if (!result.success) {
      return `❌ ${result.error}`;
    }

    const { score, status, active_loans, credit_history_years } = result.data!;
    const band = getCreditScoreBand(score);

    let emoji = '✅';
    if (score < 650) emoji = '⚠️';
    else if (score < 700) emoji = '🟡';

    return `${emoji} Credit Score: ${score} (${band})
    
📊 Credit Assessment:
• Status: ${status}
• Active Loans: ${active_loans}
• Credit History: ${credit_history_years} years

Your credit profile has been analyzed successfully!`;
  }

  /**
   * Evaluate if credit score meets minimum requirements
   */
  meetsMinimumRequirement(score: number): boolean {
    return score >= 650;
  }
}