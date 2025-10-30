/* eslint-disable @typescript-eslint/no-explicit-any */
// ============================================================================
// ORCHESTRATOR - Routes user messages to appropriate agents
// Path: loan-agent-system/lib/agents/orchestrator.ts
// ============================================================================

import { ConversationState, ConversationStage, OrchestratorInput, OrchestratorOutput, ChatMessage } from '@/types';
import { KYCAgent } from './kyc-agent';
import { CreditAgent } from './credit-agent';
import { UnderwritingAgent } from './underwriting-agent';
import { extractIntent } from '@/lib/groq';
import { v4 as uuidv4 } from 'uuid';

/**
 * Orchestrator Agent
 * Routes user messages to appropriate worker agents
 */
export class Orchestrator {
  private kycAgent: KYCAgent;
  private creditAgent: CreditAgent;
  private underwritingAgent: UnderwritingAgent;

  constructor() {
    this.kycAgent = new KYCAgent();
    this.creditAgent = new CreditAgent();
    this.underwritingAgent = new UnderwritingAgent();
  }

  /**
   * Process user message and route to appropriate agent
   */
  async process(input: OrchestratorInput): Promise<OrchestratorOutput> {
    const { user_message, conversation_state } = input;

    // Add user message to conversation
    const userMsg: ChatMessage = {
      id: uuidv4(),
      sender: 'user',
      message: user_message,
      timestamp: new Date(),
    };

    const updatedMessages = [...conversation_state.messages, userMsg];

    // Determine next action based on current stage
    let response = '';
    let newStage = conversation_state.stage;
    let updatedLoanData = { ...conversation_state.loan_data };
    let agentUsed = 'master';
    let kycVerified = conversation_state.kyc_verified;
    let creditChecked = conversation_state.credit_checked;

    switch (conversation_state.stage) {
      case 'greeting':
        response = await this.handleGreeting(user_message);
        newStage = 'collect_pan';
        break;

      case 'collect_pan':
        const panResult = await this.handlePANCollection(user_message);
        if (panResult.success && panResult.data) {
          updatedLoanData = {
            ...updatedLoanData,
            pan_number: panResult.data.pan_number,
            full_name: panResult.data.full_name,
            age: panResult.data.age,
            phone: panResult.data.phone,
          };
          kycVerified = true;
          newStage = 'collect_employment';
          response = panResult.response;
          agentUsed = 'kyc';
        } else {
          response = panResult.response;
          newStage = 'collect_pan';
        }
        break;

      case 'collect_employment':
        const empResult = await this.handleEmploymentCollection(user_message, conversation_state);
        updatedLoanData = { ...updatedLoanData, ...empResult.data };
        response = empResult.response;
        newStage = empResult.nextStage;
        break;

      case 'collect_income':
        const incomeResult = await this.handleIncomeCollection(user_message, conversation_state);
        updatedLoanData = { ...updatedLoanData, ...incomeResult.data };
        response = incomeResult.response;
        newStage = incomeResult.nextStage;
        break;

      case 'collect_loan_details':
        const loanResult = await this.handleLoanDetailsCollection(user_message, conversation_state);
        updatedLoanData = { ...updatedLoanData, ...loanResult.data };
        response = loanResult.response;
        newStage = loanResult.nextStage;
        break;

      case 'collect_existing_obligations':
        const emiResult = await this.handleEMICollection(user_message, conversation_state);
        updatedLoanData = { ...updatedLoanData, ...emiResult.data };
        response = emiResult.response;
        newStage = emiResult.nextStage;

        // After collecting all data, fetch credit score
        if (newStage === 'underwriting') {
          const creditResult = await this.creditAgent.checkCredit(updatedLoanData.pan_number!);
          if (creditResult.success && creditResult.data) {
            updatedLoanData.credit_score = creditResult.data.score;
            updatedLoanData.credit_status = creditResult.data.status;
            updatedLoanData.active_loans = creditResult.data.active_loans;
            creditChecked = true;

            response += '\n\n' + this.creditAgent.generateResponse(creditResult);
            response += '\n\n⏳ Analyzing your application...';
            agentUsed = 'credit';
          }
        }
        break;

      case 'underwriting':
        // Make underwriting decision
        const decision = this.underwritingAgent.evaluate(updatedLoanData);
        response = this.underwritingAgent.generateResponse(decision, updatedLoanData.full_name || 'Customer');
        
        if (decision.approved) {
          updatedLoanData.sanctioned_amount = decision.sanctioned_amount;
          updatedLoanData.interest_rate = decision.interest_rate;
          updatedLoanData.monthly_emi = decision.monthly_emi;
          newStage = 'approved';
        } else {
          newStage = 'rejected';
        }
        agentUsed = 'underwriting';
        break;

      case 'approved':
      case 'rejected':
        response = 'Your application has been processed. Thank you for using QuickLoan!';
        newStage = 'completed';
        break;

      default:
        response = 'I apologize, but something went wrong. Let me help you start a new application.';
        newStage = 'greeting';
    }

    // Add agent response to conversation
    const agentMsg: ChatMessage = {
      id: uuidv4(),
      sender: 'agent',
      message: response,
      timestamp: new Date(),
      metadata: {
        agent_type: agentUsed,
      },
    };

    const finalMessages = [...updatedMessages, agentMsg];

    return {
      response,
      updated_state: {
        ...conversation_state,
        stage: newStage,
        loan_data: updatedLoanData,
        messages: finalMessages,
        kyc_verified: kycVerified,
        credit_checked: creditChecked,
      },
      agent_used: agentUsed,
    };
  }

  // ========== Stage Handlers ==========

  private async handleGreeting(message: string): Promise<string> {
    return `👋 Welcome to QuickLoan! I'm here to help you apply for a personal loan.\n\nLet's get started! To verify your identity, could you please provide your **PAN number**?\n\n💡 Your PAN should be in the format: ABCDE1234F`;
  }

  private async handlePANCollection(message: string): Promise<{
    success: boolean;
    data?: any;
    response: string;
  }> {
    // Extract PAN from message
    const panRegex = /[A-Z]{5}[0-9]{4}[A-Z]/gi;
    const panMatch = message.match(panRegex);

    if (!panMatch) {
      return {
        success: false,
        response: `I couldn't find a valid PAN number in your message. Please provide your PAN in the format: ABCDE1234F`,
      };
    }

    const pan = panMatch[0].toUpperCase();

    // Verify with KYC Agent
    const kycResult = await this.kycAgent.verify(pan);

    if (!kycResult.success) {
      return {
        success: false,
        response: this.kycAgent.generateResponse(kycResult),
      };
    }

    const successResponse = this.kycAgent.generateResponse(kycResult);
    const nextQuestion = `\n\nNow, let's talk about your employment. Are you:\n1️⃣ Salaried\n2️⃣ Self-Employed\n3️⃣ Business Owner`;

    return {
      success: true,
      data: kycResult.data,
      response: successResponse + nextQuestion,
    };
  }

  private async handleEmploymentCollection(
    message: string,
    state: ConversationState
  ): Promise<{ data: any; response: string; nextStage: ConversationStage }> {
    const lowerMsg = message.toLowerCase();
    let employmentType: string | undefined;

    if (lowerMsg.includes('salaried') || lowerMsg.includes('1')) {
      employmentType = 'Salaried';
    } else if (lowerMsg.includes('self') || lowerMsg.includes('2')) {
      employmentType = 'Self-Employed';
    } else if (lowerMsg.includes('business') || lowerMsg.includes('3')) {
      employmentType = 'Business Owner';
    }

    if (!employmentType) {
      return {
        data: {},
        response: 'Please choose:\n1️⃣ Salaried\n2️⃣ Self-Employed\n3️⃣ Business Owner',
        nextStage: 'collect_employment',
      };
    }

    return {
      data: { employment_type: employmentType as any },
      response: `Great! You're ${employmentType}.\n\nWhat is your **monthly income** in rupees?`,
      nextStage: 'collect_income',
    };
  }

  private async handleIncomeCollection(
    message: string,
    state: ConversationState
  ): Promise<{ data: any; response: string; nextStage: ConversationStage }> {
    // Extract number from message
    const numberMatch = message.match(/[\d,]+/);
    if (!numberMatch) {
      return {
        data: {},
        response: 'Please enter your monthly income as a number (e.g., 50000)',
        nextStage: 'collect_income',
      };
    }

    const income = parseInt(numberMatch[0].replace(/,/g, ''));

    if (income < 10000) {
      return {
        data: {},
        response: 'The income seems too low. Please enter your monthly income in rupees (e.g., 50000)',
        nextStage: 'collect_income',
      };
    }

    return {
      data: { monthly_income: income },
      response: `Monthly income of ₹${income.toLocaleString('en-IN')} noted!\n\nNow, let's discuss the loan:\n• **How much loan amount** do you need?\n• **What is the purpose** of this loan?\n• **Preferred tenure** (in months, e.g., 12, 24, 36)?`,
      nextStage: 'collect_loan_details',
    };
  }

  private async handleLoanDetailsCollection(
    message: string,
    state: ConversationState
  ): Promise<{ data: any; response: string; nextStage: ConversationStage }> {
    const data: any = {};

    // Extract loan amount
    const amountMatch = message.match(/[\d,]+/);
    if (amountMatch) {
      data.loan_amount_requested = parseInt(amountMatch[0].replace(/,/g, ''));
    }

    // Extract tenure
    const tenureMatch = message.match(/(\d+)\s*(month|months|mo)/i);
    if (tenureMatch) {
      data.preferred_tenure = parseInt(tenureMatch[1]);
    }

    // Extract purpose (simple keywords)
    const lowerMsg = message.toLowerCase();
    if (lowerMsg.includes('wedding')) data.loan_purpose = 'Wedding';
    else if (lowerMsg.includes('education')) data.loan_purpose = 'Education';
    else if (lowerMsg.includes('medical')) data.loan_purpose = 'Medical';
    else if (lowerMsg.includes('home') || lowerMsg.includes('renovation'))
      data.loan_purpose = 'Home Renovation';
    else if (lowerMsg.includes('business')) data.loan_purpose = 'Business';

    // Check if we have all required fields
    if (!data.loan_amount_requested || !data.preferred_tenure || !data.loan_purpose) {
      return {
        data: {},
        response:
          'Please provide:\n1. Loan amount (e.g., 500000)\n2. Purpose (wedding/education/medical/home renovation/business)\n3. Tenure in months (e.g., 36)',
        nextStage: 'collect_loan_details',
      };
    }

    return {
      data,
      response: `Perfect! Loan details captured:\n• Amount: ₹${data.loan_amount_requested.toLocaleString(
        'en-IN'
      )}\n• Purpose: ${data.loan_purpose}\n• Tenure: ${data.preferred_tenure} months\n\nLast question: Do you have any **existing monthly EMIs** from other loans? If yes, what's the total monthly EMI amount? If no, just say 0.`,
      nextStage: 'collect_existing_obligations',
    };
  }

  private async handleEMICollection(
    message: string,
    state: ConversationState
  ): Promise<{ data: any; response: string; nextStage: ConversationStage }> {
    const numberMatch = message.match(/[\d,]+/);
    const existingEMI = numberMatch ? parseInt(numberMatch[0].replace(/,/g, '')) : 0;

    return {
      data: { existing_emi: existingEMI },
      response: `Existing EMI: ₹${existingEMI.toLocaleString('en-IN')} noted.\n\n📊 Fetching your credit score...`,
      nextStage: 'underwriting',
    };
  }
}