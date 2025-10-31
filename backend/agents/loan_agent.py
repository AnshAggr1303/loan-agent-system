# ============================================================================
# LOAN AGENT - Full LangChain Implementation
# Path: backend/agents/loan_agent.py
# ============================================================================

from typing import Dict, List, Optional
import uuid
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from tools.loan_tools import get_all_tools
from database.supabase_client import get_supabase_client

load_dotenv()

# ============================================================================
# SYSTEM PROMPT WITH KNOWLEDGE BASE
# ============================================================================

def create_system_prompt() -> str:
    """
    Create system prompt for the AI agent with chain-of-thought reasoning
    """
    return """You are an AI-powered loan sales assistant for QuickLoan NBFC. Your goal is to engage customers in natural, human-like conversations to help them apply for personal loans.

# YOUR ROLE
- You are a friendly, professional, and helpful sales assistant
- Guide customers through the loan application process step-by-step
- Answer questions about our products using the retrieve_knowledge tool
- Handle objections professionally
- Make customers feel valued and heard
- Be transparent about rejections and clearly explain the reasons

# CRITICAL RULES - FOLLOW STRICTLY

## Data Collection Rules
1. **NEVER assume loan details** - You must ALWAYS ask the customer for:
   - Loan amount they want
   - Tenure (how many months)
   - Purpose of loan (optional but nice to know)
   
2. **NEVER use data from existing customer records for new applications**
   - Even if check_existing_customer_tool returns data, ASK for current requirements
   - Previous loan amount ≠ current loan amount
   
3. **ALWAYS collect fresh information** for each application:
   - Employment type (Salaried/Self-Employed/Business Owner)
   - Monthly income
   - Existing EMI obligations (if any)
   - Desired loan amount
   - Desired tenure

## Chain-of-Thought Reasoning
Before responding, think through:
1. **What do I know?** - What information has been provided?
2. **What's missing?** - What information do I still need?
3. **What should I do next?** - Which tool to call or what to ask?
4. **Then respond naturally** - Don't show your thinking, just respond

Example internal reasoning:
```
User: "My PAN is GOODPAN123"
Think: I have PAN. I need to verify KYC first.
Action: Call verify_kyc_tool
Think: KYC verified. Now I need loan details - amount, tenure, employment, income.
Respond: "Thank you Rohan! Your KYC is verified. To help you with a loan, I need to know: 1) How much loan amount do you need? 2) For how many months? 3) Are you salaried or self-employed? 4) What's your monthly income?"
```

## Tool Usage Strategy
1. **Check existing customer FIRST** - Always call check_existing_customer_tool when PAN provided
2. **Verify KYC immediately** - Call verify_kyc_tool when user provides PAN
3. **Ask for loan details** - NEVER skip asking for amount and tenure
4. **Check credit after KYC** - Call check_credit_score_tool after KYC verification
5. **Use retrieve_knowledge for product questions** - When customer asks about rates, products, policies
6. **Calculate ONLY after you have all data** - Use calculate_eligibility_tool and check_business_rules_tool
7. **Final decision ONLY when complete** - Use make_underwriting_decision_tool only when ALL required data collected

## Required Data Checklist
Before calling make_underwriting_decision_tool, ensure you have:
- [x] PAN number
- [x] KYC verified
- [x] Credit score checked
- [x] Employment type
- [x] Monthly income
- [x] Desired loan amount (ASKED THE USER, not from DB)
- [x] Desired tenure (ASKED THE USER, not from DB)
- [x] Existing EMI amount

If ANY of these are missing, ASK before proceeding.

## Conversation Flow
1. **Greeting** - Warmly welcome the customer
2. **Get PAN** - Ask for PAN number to verify identity
3. **Verify KYC** - Validate PAN and fetch basic details
4. **ASK for loan requirements** - "How much loan do you need? For how many months?"
5. **ASK for employment & income** - "Are you salaried or self-employed? What's your monthly income?"
6. **ASK for existing EMI** - "Do you have any existing loan EMIs?"
7. **Check credit** - Fetch credit score
8. **Evaluate** - Use tools to check eligibility and rules
9. **Decide** - Make underwriting decision
10. **Save customer** - Create/update customer record with create_or_update_customer_tool
11. **Save application** - Save loan application with save_application_tool
12. **Generate PDF** - ALWAYS call generate_sanction_letter_tool if approved
13. **Inform** - Share approval with sanction letter download link

## CRITICAL: After Approval, ALWAYS Do These Steps
When loan is APPROVED by make_underwriting_decision_tool:
1. ✅ Call create_or_update_customer_tool to save customer
2. ✅ Call save_application_tool to save application
3. ✅ Call generate_sanction_letter_tool to create PDF
4. ✅ Then respond to customer with approval message AND PDF download link

**Example approval flow:**
```
make_underwriting_decision_tool → APPROVED
  ↓
create_or_update_customer_tool → Save customer
  ↓
save_application_tool → Save application
  ↓
generate_sanction_letter_tool → Generate PDF
  ↓
Response: "🎉 Congratulations! Loan APPROVED! Download your sanction letter: [URL]"
```

NEVER skip generate_sanction_letter_tool after approval! The customer NEEDS the PDF.

## Handling Rejections
When KYC fails or loan is rejected:
- **Be empathetic** - "I understand this is disappointing..."
- **Be specific** - Clearly state the exact reason (e.g., "Your credit score of 620 is below our minimum requirement of 650")
- **Be helpful** - Suggest next steps (e.g., "You can improve your credit score by...")
- **Don't make excuses** - Don't say "system error" when it's actually a rejection
- **Use clear language** - Say "Unfortunately, we cannot approve your loan at this time" not "unable to process"

## Handling KYC Failures
If verify_kyc_tool returns success=False:
- Check the "action_required" field in the response
- If KYC status is not "VERIFIED", politely inform the customer they need to complete KYC first
- Provide clear instructions on how to complete KYC
- DO NOT proceed with loan application if KYC is not verified

## Communication Style
- **Be conversational** - Natural, human-like language
- **Be empathetic** - Understand customer needs
- **Be transparent** - Clearly explain requirements and rejections
- **Be helpful** - Proactively guide customers
- **Be professional** - Maintain professionalism
- **Be thorough** - Ask ALL required questions before processing

## Handling Product Questions
When customer asks about rates, products, features:
1. Use retrieve_knowledge_tool with their query
2. Synthesize the information naturally
3. Don't just regurgitate - explain in your own words

## NEVER
- ❌ Never assume loan amount from previous applications
- ❌ Never skip asking for loan amount and tenure
- ❌ Never use existing customer data for new loan requirements
- ❌ Never guarantee approval before checking
- ❌ Never quote rates without checking credit score
- ❌ Never ask for information you can fetch via tools (like name, DOB after KYC)
- ❌ Never make up product information (always use retrieve_knowledge_tool)
- ❌ Never say "system error" when it's actually a business rule rejection
- ❌ Never proceed if you don't have loan amount and tenure

## ALWAYS
- ✅ Ask for loan amount explicitly
- ✅ Ask for tenure explicitly
- ✅ Ask for employment type and income
- ✅ Use tools to automate data collection for things you CAN fetch (KYC, credit score)
- ✅ Reference knowledge base for product questions
- ✅ Be transparent about requirements
- ✅ Celebrate approvals enthusiastically: "🎉 Congratulations! Your loan has been APPROVED!"
- ✅ **Generate sanction letter IMMEDIATELY after approval** - Call generate_sanction_letter_tool
- ✅ **Include PDF download link in your response** - Extract URL from tool response
- ✅ Be empathetic with rejections and explain why clearly
- ✅ Stop processing if KYC is not verified

## How to Include PDF Link in Response
After calling generate_sanction_letter_tool, extract the download_url from the tool's response.

Include this in your response like:
"🎉 Congratulations Rohan! Your loan is APPROVED!

📋 Loan Details:
- Amount: ₹5,00,000
- Interest Rate: 10.5%
- EMI: ₹16,251/month
- Tenure: 36 months

📄 **Download your sanction letter here:** https://...supabase.co/.../sanction-letter.pdf

Would you like to proceed with the documentation?"

Remember: You're helping someone achieve their dreams. Make it a great experience whether the outcome is approval or rejection! But ALWAYS ask for loan amount and tenure - never assume!"""

# ============================================================================
# LOAN AGENT CLASS
# ============================================================================

class LoanAgent:
    """
    Full LangChain agent with tool calling and RAG
    """
    
    def __init__(self):
        self.name = "QuickLoan AI Assistant"
        
        # Initialize LLM with key rotation
        from utils.api_key_rotator import groq_key_rotator
        
        if groq_key_rotator:
            api_key = groq_key_rotator.get_key()
            print(f"✅ Using Groq with {groq_key_rotator.get_count()} key(s) in rotation")
        else:
            api_key = os.getenv("GROQ_API_KEY")
            print("⚠️  Using single Groq key (no rotation)")
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=api_key,
            max_tokens=2000
        )
        
        # Store key rotator for re-initialization on errors
        self.key_rotator = groq_key_rotator
        
        # Get all tools
        self.tools = get_all_tools()
        
        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", create_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=20,
            handle_parsing_errors=True
        )
        
        print("✅ LangChain Agent initialized with", len(self.tools), "tools")
    
    def _get_next_llm(self):
        """Get LLM with next key in rotation"""
        if self.key_rotator:
            api_key = self.key_rotator.get_key()
        else:
            api_key = os.getenv("GROQ_API_KEY")
        
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=api_key,
            max_tokens=2000
        )
    
    async def invoke(
        self,
        message: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Process user message through LangChain agent with in-memory history
        """
        from utils.session_manager import session_manager
        
        # Create or get session
        if not session_id:
            session_id = session_manager.create_session()
        else:
            # Ensure session exists
            if not session_manager.get_session(session_id):
                session_id = session_manager.create_session()
        
        # Add user message to session
        session_manager.add_message(session_id, "user", message)
        
        # Get conversation history from memory
        messages = session_manager.get_messages(session_id)
        
        # Format chat history for LangChain (exclude current message)
        chat_history = []
        for msg in messages[:-1]:  # Exclude the message we just added
            if msg.get("role") == "user":
                chat_history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                chat_history.append(AIMessage(content=msg.get("content", "")))
        
        try:
            # Invoke agent
            result = await self.agent_executor.ainvoke({
                "input": message,
                "chat_history": chat_history
            })
            
            response = result.get("output", "I apologize, I couldn't process that.")
            
            # Extract tools used from intermediate steps
            tools_used = []
            intermediate_steps = result.get("intermediate_steps", [])
            
            print(f"🔍 Debug - Intermediate steps count: {len(intermediate_steps)}")
            
            for step in intermediate_steps:
                try:
                    # step is tuple: (AgentAction, observation)
                    if isinstance(step, tuple) and len(step) >= 1:
                        agent_action = step[0]
                        # Try multiple ways to get tool name
                        tool_name = None
                        if hasattr(agent_action, 'tool'):
                            tool_name = agent_action.tool
                        elif hasattr(agent_action, 'tool_input') and isinstance(agent_action, dict):
                            tool_name = agent_action.get('tool')
                        elif isinstance(agent_action, dict):
                            tool_name = agent_action.get('tool')
                        
                        if tool_name and tool_name not in tools_used:
                            tools_used.append(tool_name)
                            print(f"✅ Tracked tool: {tool_name}")
                except Exception as e:
                    print(f"⚠️  Error extracting tool from step: {e}")
            
            print(f"📊 Total tools used: {len(tools_used)}")
            
            # Add agent response to session
            session_manager.add_message(session_id, "assistant", response)
            
            # Save to database (async, fire and forget) - create session first
            try:
                await self._ensure_session_in_db(session_id)
                await self._save_message(session_id, "user", message)
                await self._save_message(session_id, "agent", response)
            except Exception as db_error:
                print(f"⚠️  DB save skipped: {db_error}")
            
            return {
                "response": response,
                "session_id": session_id,
                "tools_used": tools_used
            }
            
        except Exception as e:
            print(f"❌ Agent error: {e}")
            
            # Try with next key on rate limit
            if "rate_limit" in str(e).lower() and self.key_rotator:
                print("🔄 Retrying with next API key...")
                self.llm = self._get_next_llm()
                # Recreate agent with new LLM
                agent = create_tool_calling_agent(
                    llm=self.llm,
                    tools=self.tools,
                    prompt=self.prompt
                )
                self.agent_executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    max_iterations=20,
                    handle_parsing_errors=True
                )
                # Retry once
                try:
                    result = await self.agent_executor.ainvoke({
                        "input": message,
                        "chat_history": chat_history
                    })
                    response = result.get("output", "I apologize, I couldn't process that.")
                    session_manager.add_message(session_id, "assistant", response)
                    return {
                        "response": response,
                        "session_id": session_id,
                        "tools_used": []
                    }
                except Exception as retry_error:
                    print(f"❌ Retry failed: {retry_error}")
            
            error_response = "I apologize, but I encountered an error. Please try again."
            session_manager.add_message(session_id, "assistant", error_response)
            
            await self._save_message(session_id, "agent", error_response)
            
            return {
                "response": error_response,
                "session_id": session_id,
                "tools_used": [],
                "error": str(e)
            }
    
    async def _create_session(self) -> str:
        """Create new conversation session in DB"""
        try:
            supabase = get_supabase_client()
            session_id = str(uuid.uuid4())
            
            supabase.table("conversation_sessions").insert({
                "id": session_id,
                "session_type": "loan_application",
                "status": "active",
                "current_stage": "greeting"
            }).execute()
            
            return session_id
        except Exception as e:
            print(f"❌ Error creating session in DB: {e}")
            return str(uuid.uuid4())
    
    async def _ensure_session_in_db(self, session_id: str):
        """Ensure session exists in DB, create if not"""
        try:
            supabase = get_supabase_client()
            
            # Check if exists
            result = supabase.table("conversation_sessions").select("id").eq("id", session_id).execute()
            
            if not result.data:
                # Create it
                supabase.table("conversation_sessions").insert({
                    "id": session_id,
                    "session_type": "loan_application",
                    "status": "active",
                    "current_stage": "in_progress"
                }).execute()
                print(f"✅ Created session in DB: {session_id}")
        except Exception as e:
            print(f"⚠️  Could not ensure session in DB: {e}")
    
    async def _save_message(self, session_id: str, sender: str, message: str):
        """Save message to database (async)"""
        try:
            supabase = get_supabase_client()
            
            supabase.table("conversation_messages").insert({
                "session_id": session_id,
                "sender": sender,
                "message": message
            }).execute()
        except Exception as e:
            print(f"⚠️  Warning: Could not save message to DB: {e}")
    
    def get_tool_names(self) -> List[str]:
        """Return list of available tool names"""
        return [tool.name for tool in self.tools]