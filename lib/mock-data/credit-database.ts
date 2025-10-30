// ============================================================================
// MOCK CREDIT BUREAU DATABASE - Simulates CIBIL/Experian credit data
// ============================================================================

export interface MockCreditRecord {
  pan_number: string;
  score: number;
  status: string;
  active_loans: number;
  credit_history_years: number;
  defaults: number;
  late_payments_6m: number;
  credit_utilization: number; // percentage
}

export const MOCK_CREDIT_DATABASE: Record<string, MockCreditRecord> = {
  // ========== Excellent Credit (750+) ==========
  "GOODPAN123": {
    pan_number: "GOODPAN123",
    score: 790,
    status: "No defaults",
    active_loans: 1,
    credit_history_years: 8,
    defaults: 0,
    late_payments_6m: 0,
    credit_utilization: 25
  },
  
  "ABCDE1234F": {
    pan_number: "ABCDE1234F",
    score: 820,
    status: "Excellent payment history",
    active_loans: 2,
    credit_history_years: 10,
    defaults: 0,
    late_payments_6m: 0,
    credit_utilization: 20
  },
  
  "PQRST3456U": {
    pan_number: "PQRST3456U",
    score: 810,
    status: "No defaults",
    active_loans: 1,
    credit_history_years: 7,
    defaults: 0,
    late_payments_6m: 0,
    credit_utilization: 30
  },
  
  // ========== Good Credit (700-750) ==========
  "FGHIJ5678K": {
    pan_number: "FGHIJ5678K",
    score: 720,
    status: "Good payment history",
    active_loans: 2,
    credit_history_years: 5,
    defaults: 0,
    late_payments_6m: 1,
    credit_utilization: 40
  },
  
  "KYCFAIL789": {
    pan_number: "KYCFAIL789",
    score: 760,
    status: "No defaults",
    active_loans: 0,
    credit_history_years: 10,
    defaults: 0,
    late_payments_6m: 0,
    credit_utilization: 15
  },
  
  "UVWXY7890Z": {
    pan_number: "UVWXY7890Z",
    score: 740,
    status: "Stable credit behavior",
    active_loans: 3,
    credit_history_years: 6,
    defaults: 0,
    late_payments_6m: 0,
    credit_utilization: 35
  },
  
  "AAAAA1111A": {
    pan_number: "AAAAA1111A",
    score: 730,
    status: "Good",
    active_loans: 1,
    credit_history_years: 5,
    defaults: 0,
    late_payments_6m: 1,
    credit_utilization: 45
  },
  
  // ========== Average Credit (650-700) ==========
  "BADPAN456": {
    pan_number: "BADPAN456",
    score: 680,
    status: "2x 60-day late payments",
    active_loans: 3,
    credit_history_years: 5,
    defaults: 0,
    late_payments_6m: 2,
    credit_utilization: 60
  },
  
  "KLMNO9012P": {
    pan_number: "KLMNO9012P",
    score: 670,
    status: "Some late payments",
    active_loans: 4,
    credit_history_years: 4,
    defaults: 0,
    late_payments_6m: 3,
    credit_utilization: 65
  },
  
  // ========== Poor Credit (<650) ==========
  "BBBBB2222B": {
    pan_number: "BBBBB2222B",
    score: 620,
    status: "Multiple late payments, 1 default",
    active_loans: 5,
    credit_history_years: 3,
    defaults: 1,
    late_payments_6m: 4,
    credit_utilization: 85
  }
};

/**
 * Simulate credit score fetch with realistic delay
 */
export async function fetchCreditScore(pan: string): Promise<MockCreditRecord | null> {
  // Simulate API delay (credit bureaus are slower)
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  const record = MOCK_CREDIT_DATABASE[pan.toUpperCase()];
  return record || null;
}

/**
 * Categorize credit score into bands
 */
export function getCreditScoreBand(score: number): string {
  if (score >= 800) return 'Excellent';
  if (score >= 750) return 'Very Good';
  if (score >= 700) return 'Good';
  if (score >= 650) return 'Fair';
  return 'Poor';
}

/**
 * Determine risk level based on credit data
 */
export function calculateRiskLevel(creditData: MockCreditRecord): 'Low' | 'Medium' | 'High' {
  const { score, defaults, late_payments_6m, credit_utilization } = creditData;
  
  // High risk criteria
  if (score < 650 || defaults > 0 || late_payments_6m >= 3 || credit_utilization > 75) {
    return 'High';
  }
  
  // Low risk criteria
  if (score >= 750 && defaults === 0 && late_payments_6m === 0 && credit_utilization <= 30) {
    return 'Low';
  }
  
  // Everything else is medium risk
  return 'Medium';
}