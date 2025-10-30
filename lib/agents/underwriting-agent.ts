// ============================================================================
// UNDERWRITING AGENT - Rule-Based Loan Approval
// Path: loan-agent-system/lib/agents/underwriting-agent.ts
// ============================================================================

import { LoanApplicationData, UnderwritingDecision, EmploymentType } from '@/types';
import { calculateEMI, calculateDTI, calculateInterestRate, calculateProcessingFee } from '@/lib/utils/calculations';

/**
 * Underwriting Agent
 * Makes loan approval decisions based on business rules
 */
export class UnderwritingAgent {
  private readonly RULES = {
    MIN_AGE: 21,
    MAX_AGE: 60,
    MIN_INCOME_SALARIED: 25000,
    MIN_INCOME_SELF_EMPLOYED: 40000,
    MIN_CREDIT_SCORE: 650,
    MAX_DTI_RATIO: 0.50, // 50%
    MAX_LOAN_MULTIPLIER_SALARIED: 10,
    MAX_LOAN_MULTIPLIER_SELF_EMPLOYED: 5,
  };

  /**
   * Evaluate loan application using business rules
   */
  evaluate(data: LoanApplicationData): UnderwritingDecision {
    const failedRules: string[] = [];

    // ========== Rule 1: Age Constraint ==========
    if (!data.age || data.age < this.RULES.MIN_AGE) {
      failedRules.push(`Minimum age requirement: ${this.RULES.MIN_AGE} years`);
    }
    if (data.age && data.age > this.RULES.MAX_AGE) {
      failedRules.push(`Maximum age limit: ${this.RULES.MAX_AGE} years`);
    }

    // ========== Rule 2: Minimum Income ==========
    const minIncome =
      data.employment_type === 'Salaried'
        ? this.RULES.MIN_INCOME_SALARIED
        : this.RULES.MIN_INCOME_SELF_EMPLOYED;

    if (!data.monthly_income || data.monthly_income < minIncome) {
      failedRules.push(
        `Minimum monthly income: ₹${minIncome.toLocaleString('en-IN')} for ${data.employment_type}`
      );
    }

    // ========== Rule 3: Credit Score ==========
    if (!data.credit_score || data.credit_score < this.RULES.MIN_CREDIT_SCORE) {
      failedRules.push(`Minimum credit score required: ${this.RULES.MIN_CREDIT_SCORE}`);
    }

    // ========== Rule 4: DTI Ratio ==========
    if (data.monthly_income && data.loan_amount_requested && data.preferred_tenure) {
      const interestRate = calculateInterestRate(data.credit_score || 650);
      const estimatedEMI = calculateEMI(
        data.loan_amount_requested,
        interestRate,
        data.preferred_tenure
      );

      const existingEMI = data.existing_emi || 0;
      const dtiRatio = calculateDTI(existingEMI, estimatedEMI, data.monthly_income);

      if (dtiRatio > this.RULES.MAX_DTI_RATIO * 100) {
        failedRules.push(
          `Debt-to-Income ratio (${dtiRatio.toFixed(1)}%) exceeds maximum allowed (${
            this.RULES.MAX_DTI_RATIO * 100
          }%)`
        );
      }
    }

    // ========== Rule 5: Maximum Loan Amount ==========
    if (data.monthly_income && data.loan_amount_requested) {
      const multiplier =
        data.employment_type === 'Salaried'
          ? this.RULES.MAX_LOAN_MULTIPLIER_SALARIED
          : this.RULES.MAX_LOAN_MULTIPLIER_SELF_EMPLOYED;

      const maxLoanAmount = data.monthly_income * multiplier;

      if (data.loan_amount_requested > maxLoanAmount) {
        failedRules.push(
          `Maximum loan amount for your income: ₹${maxLoanAmount.toLocaleString('en-IN')}`
        );
      }
    }

    // ========== Decision ==========
    if (failedRules.length > 0) {
      // REJECTED
      return {
        approved: false,
        rejection_reason: 'Application does not meet eligibility criteria',
        failed_rules: failedRules,
      };
    }

    // APPROVED - Calculate loan terms
    const interestRate = calculateInterestRate(data.credit_score!);
    const monthlyEMI = calculateEMI(
      data.loan_amount_requested!,
      interestRate,
      data.preferred_tenure!
    );
    const existingEMI = data.existing_emi || 0;
    const dtiRatio = calculateDTI(existingEMI, monthlyEMI, data.monthly_income!);

    return {
      approved: true,
      sanctioned_amount: data.loan_amount_requested!,
      interest_rate: interestRate,
      monthly_emi: monthlyEMI,
      tenure: data.preferred_tenure!,
      dti_ratio: dtiRatio,
    };
  }

  /**
   * Generate natural language response for underwriting decision
   */
  generateResponse(decision: UnderwritingDecision, customerName: string): string {
    if (!decision.approved) {
      let response = `❌ Sorry ${customerName}, we're unable to approve your loan application at this time.\n\n`;
      response += `**Reason:** ${decision.rejection_reason}\n\n`;
      response += `**Requirements not met:**\n`;
      decision.failed_rules?.forEach((rule) => {
        response += `• ${rule}\n`;
      });
      response += `\n💡 **What you can do:**\n`;
      response += `• Improve your credit score\n`;
      response += `• Reduce existing debt obligations\n`;
      response += `• Apply for a smaller loan amount\n`;
      response += `\nWe encourage you to reapply after addressing these requirements.`;

      return response;
    }

    // APPROVED
    const processingFee = calculateProcessingFee(decision.sanctioned_amount!);
    let response = `🎉 **Congratulations ${customerName}!** Your loan has been **APPROVED**!\n\n`;
    response += `📋 **Loan Details:**\n`;
    response += `• **Sanctioned Amount:** ₹${decision.sanctioned_amount!.toLocaleString('en-IN')}\n`;
    response += `• **Interest Rate:** ${decision.interest_rate}% per annum\n`;
    response += `• **Tenure:** ${decision.tenure} months\n`;
    response += `• **Monthly EMI:** ₹${decision.monthly_emi!.toLocaleString('en-IN')}\n`;
    response += `• **Processing Fee:** ₹${processingFee.toLocaleString('en-IN')}\n`;
    response += `• **Your DTI Ratio:** ${decision.dti_ratio!.toFixed(1)}%\n\n`;

    response += `📄 Generating your sanction letter...`;

    return response;
  }

  /**
   * Calculate counter offer for rejected applications
   */
  calculateCounterOffer(data: LoanApplicationData): number | null {
    if (!data.monthly_income) return null;

    const multiplier =
      data.employment_type === 'Salaried'
        ? this.RULES.MAX_LOAN_MULTIPLIER_SALARIED
        : this.RULES.MAX_LOAN_MULTIPLIER_SELF_EMPLOYED;

    const maxAmount = data.monthly_income * multiplier;
    const counterOffer = Math.min(maxAmount, (data.loan_amount_requested || 0) * 0.6);

    return Math.floor(counterOffer / 10000) * 10000; // Round down to nearest 10k
  }
}