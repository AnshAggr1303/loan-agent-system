// ============================================================================
// CALCULATION UTILITIES - EMI, DTI, Interest Rate calculations
// ============================================================================

/**
 * Calculate EMI (Equated Monthly Installment)
 * Formula: EMI = [P × R × (1+R)^N] / [(1+R)^N-1]
 * Where:
 * P = Principal loan amount
 * R = Monthly interest rate (annual rate / 12 / 100)
 * N = Tenure in months
 */
export function calculateEMI(
  principal: number,
  annualRate: number,
  tenureMonths: number
): number {
  const monthlyRate = annualRate / 12 / 100;
  
  if (monthlyRate === 0) {
    return principal / tenureMonths;
  }
  
  const emi = 
    (principal * monthlyRate * Math.pow(1 + monthlyRate, tenureMonths)) /
    (Math.pow(1 + monthlyRate, tenureMonths) - 1);
  
  return Math.round(emi * 100) / 100; // Round to 2 decimal places
}

/**
 * Calculate Debt-to-Income Ratio
 * DTI = (Total Monthly Debt Payments / Gross Monthly Income) × 100
 */
export function calculateDTI(
  existingEMI: number,
  newEMI: number,
  monthlyIncome: number
): number {
  const totalDebt = existingEMI + newEMI;
  const dti = (totalDebt / monthlyIncome) * 100;
  return Math.round(dti * 100) / 100;
}

/**
 * Calculate Fixed Obligation to Income Ratio (FOIR)
 * Similar to DTI but includes rent and other fixed obligations
 */
export function calculateFOIR(
  existingEMI: number,
  newEMI: number,
  monthlyRent: number,
  monthlyIncome: number
): number {
  const totalObligations = existingEMI + newEMI + monthlyRent;
  const foir = (totalObligations / monthlyIncome) * 100;
  return Math.round(foir * 100) / 100;
}

/**
 * Calculate interest rate based on credit score and risk
 * Better credit score = lower interest rate
 */
export function calculateInterestRate(creditScore: number): number {
  if (creditScore >= 800) return 10.5;  // Excellent
  if (creditScore >= 750) return 11.5;  // Very Good
  if (creditScore >= 700) return 12.5;  // Good
  if (creditScore >= 650) return 14.0;  // Fair
  return 16.0;  // Poor
}

/**
 * Calculate processing fee (typically 1-2% of loan amount)
 */
export function calculateProcessingFee(loanAmount: number): number {
  const feePercentage = 1.0; // 1%
  const minFee = 1000;
  const maxFee = 10000;
  
  const fee = (loanAmount * feePercentage) / 100;
  return Math.max(minFee, Math.min(fee, maxFee));
}

/**
 * Calculate maximum eligible loan amount
 * Based on income multiplier method
 */
export function calculateMaxLoanAmount(
  monthlyIncome: number,
  employmentType: string
): number {
  // Salaried: up to 10x monthly income
  // Self-employed: up to 5x monthly income
  const multiplier = employmentType === 'Salaried' ? 10 : 5;
  return monthlyIncome * multiplier;
}

/**
 * Calculate total interest payable over loan tenure
 */
export function calculateTotalInterest(
  principal: number,
  monthlyEMI: number,
  tenureMonths: number
): number {
  const totalPayment = monthlyEMI * tenureMonths;
  const totalInterest = totalPayment - principal;
  return Math.round(totalInterest * 100) / 100;
}

/**
 * Calculate age from date of birth
 */
export function calculateAge(dateOfBirth: string): number {
  const today = new Date();
  const birthDate = new Date(dateOfBirth);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age;
}

/**
 * Format currency in Indian Rupees
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format percentage
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Validate PAN number format
 */
export function isValidPAN(pan: string): boolean {
  const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/;
  return panRegex.test(pan.toUpperCase());
}

/**
 * Validate phone number format (Indian)
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^[6-9]\d{9}$/;
  return phoneRegex.test(phone);
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}