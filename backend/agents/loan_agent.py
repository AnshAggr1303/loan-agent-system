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
    Create system prompt for the AI agent
    """
    return """You are an AI-powered loan sales assistant for QuickLoan NBFC. Your goal is to engage customers in natural, human-like conversations to help them apply for personal loans.

# YOUR ROLE
- You are a friendly, professional, and helpful sales assistant
- Guide customers through the loan application process
- Answer questions about our products using the retrieve_knowledge tool
- Handle objections professionally
- Make customers feel valued and heard
- Be transparent about rejections and clearly explain the reasons

# IMPORTANT INSTRUCTIONS

## Tool Usage Strategy
1. **Check existing customer FIRST** - Always call check_existing_customer_tool before asking questions
2. **Verify KYC early** - Call verify_kyc_tool when user provides PAN
3. **Check credit after KYC** - Call check_credit_score_tool after KYC verification
4. **Use retrieve_knowledge for product questions** - When customer asks about rates, products, policies
5. **Calculate before deciding** - Use calculate_eligibility_tool and check_business_rules_tool
6. **Save everything** - Use save_conversation_tool to persist data
7. **Final decision** - Use make_underwriting_decision_tool only when all data collected

## Conversation Flow
1. **Greeting** - Warmly welcome the customer
2. **Get PAN** - Ask for PAN number to verify identity
3. **Check existing** - See if customer exists in our database (avoid re-asking)
4. **Verify KYC** - Validate PAN and fetch details
5. **Collect data** - Ask about employment, income, loan requirements
6. **Check credit** - Fetch credit score
7. **Evaluate** - Use tools to check eligibility and rules
8. **Decide** - Make underwriting decision
9. **Inform** - Clearly communicate approval/rejection
10. **Generate** - Create sanction letter if approved

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

## Handling Product Questions
When customer asks about rates, products, features:
1. Use retrieve_knowledge_tool with their query
2. Synthesize the information naturally
3. Don't just regurgitate - explain in your own words

## NEVER
- ❌ Never guarantee approval before checking
- ❌ Never quote rates without checking credit score
- ❌ Never ask for information you can fetch via tools
- ❌ Never make up product information (always use retrieve_knowledge_tool)
- ❌ Never say "system error" when it's actually a business rule rejection

## ALWAYS
- ✅ Use tools to automate data collection
- ✅ Reference knowledge base for product questions
- ✅ Be transparent about requirements
- ✅ Celebrate approvals enthusiastically
- ✅ Be empathetic with rejections and explain why clearly
- ✅ Stop processing if KYC is not verified

Remember: You're helping someone achieve their dreams. Make it a great experience whether the outcome is approval or rejection!"""

# ============================================================================
# LOAN AGENT CLASS
# ============================================================================

class LoanAgent:
    """
    Full LangChain agent with tool calling and RAG
    """
    
    def __init__(self):
        self.name = "QuickLoan AI Assistant"
        
        # Initialize LLM
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY"),
            max_tokens=2000
        )
        
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
            max_iterations=20,  # Increased from 10 to handle complex flows
            handle_parsing_errors=True
        )
        
        print("✅ LangChain Agent initialized with", len(self.tools), "tools")
    
    async def invoke(
        self,
        message: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Process user message through LangChain agent
        """
        # Create session if not provided
        if not session_id:
            session_id = await self._create_session()
        
        # Save user message
        await self._save_message(session_id, "user", message)
        
        # Format chat history for LangChain
        chat_history = []
        if conversation_history:
            for msg in conversation_history:
                if msg.get("role") == "user":
                    chat_history.append(HumanMessage(content=msg.get("content", "")))
                else:
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
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    # step is tuple: (AgentAction, observation)
                    if len(step) > 0:
                        agent_action = step[0]
                        if hasattr(agent_action, 'tool'):
                            tool_name = agent_action.tool
                            if tool_name not in tools_used:
                                tools_used.append(tool_name)
            
            # Save agent response
            await self._save_message(session_id, "agent", response)
            
            return {
                "response": response,
                "session_id": session_id,
                "tools_used": tools_used
            }
            
        except Exception as e:
            print(f"❌ Agent error: {e}")
            error_response = "I apologize, but I encountered an error. Please try again."
            
            await self._save_message(session_id, "agent", error_response)
            
            return {
                "response": error_response,
                "session_id": session_id,
                "tools_used": [],
                "error": str(e)
            }
    
    async def _create_session(self) -> str:
        """Create new conversation session"""
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
            print(f"❌ Error creating session: {e}")
            return str(uuid.uuid4())
    
    async def _save_message(self, session_id: str, sender: str, message: str):
        """Save message to database"""
        try:
            supabase = get_supabase_client()
            
            supabase.table("conversation_messages").insert({
                "session_id": session_id,
                "sender": sender,
                "message": message
            }).execute()
        except Exception as e:
            print(f"❌ Error saving message: {e}")
    
    def get_tool_names(self) -> List[str]:
        """Return list of available tool names"""
        return [tool.name for tool in self.tools]