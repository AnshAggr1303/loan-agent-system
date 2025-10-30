/* eslint-disable @typescript-eslint/no-explicit-any */
// ============================================================================
// TYPES DEFINITION - Complete type system for Loan Agent
// ============================================================================

// ----------------------------------------------------------------------------
// User & Authentication
// ----------------------------------------------------------------------------
export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
}

// ----------------------------------------------------------------------------
// KYC Types
// ----------------------------------------------------------------------------
export interface KYCData {
  pan_number: string;
  full_name: string;
  date_of_birth: string;
  age: number;
  phone: string;
  kyc_status: 'VERIFIED' | 'PENDING' | 'FAILED';
}

export interface KYCVerificationResult {
  success: boolean;
  data?: KYCData;
  error?: string;
}

// ----------------------------------------------------------------------------
// Credit Types
// ----------------------------------------------------------------------------
export interface CreditData {
  score: number;
  status: string;
  active_loans: number;
  credit_history_years: number;
  defaults?: string;
}

export interface CreditCheckResult {
  success: boolean;
  data?: CreditData;
  error?: string;
}

// ----------------------------------------------------------------------------
// Loan Application Types
// ----------------------------------------------------------------------------
export type EmploymentType = 'Salaried' | 'Self-Employed' | 'Business Owner';
export type LoanPurpose = 'Wedding' | 'Education' | 'Medical' | 'Home Renovation' | 'Business' | 'Travel' | 'Other';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'in_progress';

export interface LoanApplicationData {
  // KYC Data
  pan_number?: string;
  full_name?: string;
  age?: number;
  phone?: string;
  
  // Employment
  employment_type?: EmploymentType;
  monthly_income?: number;
  company_name?: string;
  
  // Loan Details
  loan_amount_requested?: number;
  loan_purpose?: LoanPurpose;
  preferred_tenure?: number; // in months
  
  // Existing Obligations
  existing_emi?: number;
  has_credit_card?: boolean;
  credit_card_outstanding?: number;
  
  // Credit Data
  credit_score?: number;
  credit_status?: string;
  active_loans?: number;
  
  // Approval Data (set after underwriting)
  sanctioned_amount?: number;
  interest_rate?: number;
  monthly_emi?: number;
}

export interface LoanApplication extends LoanApplicationData {
  id: string;
  user_id: string;
  
  // Decision
  approval_status: ApprovalStatus;
  sanctioned_amount?: number;
  interest_rate?: number;
  monthly_emi?: number;
  rejection_reason?: string;
  failed_rules?: string[];
  
  // Documents
  sanction_letter_url?: string;
  
  // Metadata
  created_at: string;
  updated_at: string;
}

// ----------------------------------------------------------------------------
// Underwriting Types
// ----------------------------------------------------------------------------
export interface UnderwritingDecision {
  approved: boolean;
  sanctioned_amount?: number;
  interest_rate?: number;
  monthly_emi?: number;
  tenure?: number;
  rejection_reason?: string;
  failed_rules?: string[];
  dti_ratio?: number;
}

// ----------------------------------------------------------------------------
// Chat & Conversation Types
// ----------------------------------------------------------------------------
export type MessageSender = 'user' | 'agent';
export type ConversationStage = 
  | 'greeting'
  | 'collect_pan'
  | 'collect_phone'
  | 'collect_employment'
  | 'collect_income'
  | 'collect_loan_details'
  | 'collect_existing_obligations'
  | 'underwriting'
  | 'approved'
  | 'rejected'
  | 'completed';

export interface ChatMessage {
  id: string;
  sender: MessageSender;
  message: string;
  timestamp: Date;
  metadata?: {
    agent_type?: string;
    action?: string;
  };
}

export interface ConversationState {
  application_id?: string;
  stage: ConversationStage;
  loan_data: LoanApplicationData;
  messages: ChatMessage[];
  kyc_verified: boolean;
  credit_checked: boolean;
}

// ----------------------------------------------------------------------------
// Agent Types
// ----------------------------------------------------------------------------
export interface AgentResponse {
  success: boolean;
  message: string;
  data?: any;
  next_stage?: ConversationStage;
  requires_user_input?: boolean;
}

export interface OrchestratorInput {
  user_message: string;
  conversation_state: ConversationState;
}

export interface OrchestratorOutput {
  response: string;
  updated_state: ConversationState;
  agent_used?: string;
}

// ----------------------------------------------------------------------------
// PDF Generation Types
// ----------------------------------------------------------------------------
export interface SanctionLetterData {
  application_id: string;
  customer_name: string;
  pan_number: string;
  phone: string;
  sanctioned_amount: number;
  interest_rate: number;
  tenure: number;
  monthly_emi: number;
  processing_fee: number;
  date: string;
}

// ----------------------------------------------------------------------------
// API Response Types
// ----------------------------------------------------------------------------
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}