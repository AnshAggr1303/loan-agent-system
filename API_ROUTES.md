# 🚀 API ROUTES DOCUMENTATION

## 📋 All API Endpoints

### **Base URL:** `http://localhost:3000/api`

---

## 1️⃣ **Main Chat API**

**Endpoint:** `POST /api/chat`

**File:** `loan-agent-system/app/api/chat/route.ts`

**Purpose:** Process user messages and orchestrate conversation flow

**Request Body:**
```json
{
  "message": "I want to apply for a loan",
  "conversationState": {
    "stage": "greeting",
    "loan_data": {},
    "messages": [],
    "kyc_verified": false,
    "credit_checked": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "Welcome to QuickLoan! I'm here to help...",
  "updated_state": {
    "stage": "collect_pan",
    "loan_data": {},
    "messages": [...],
    "kyc_verified": false,
    "credit_checked": false
  },
  "agent_used": "master"
}
```

**Health Check:**
```bash
GET /api/chat
```

---

## 2️⃣ **KYC Verification API**

**Endpoint:** `POST /api/agents/kyc`

**File:** `loan-agent-system/app/api/agents/kyc/route.ts`

**Purpose:** Verify PAN and fetch customer KYC details

**Request Body:**
```json
{
  "pan": "GOODPAN123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "pan_number": "GOODPAN123",
    "full_name": "Rohan Gupta",
    "date_of_birth": "1990-05-15",
    "age": 35,
    "phone": "9876543210",
    "kyc_status": "VERIFIED"
  },
  "message": "✅ KYC Verified successfully!\n\nWelcome, Rohan Gupta!..."
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "PAN not found in our records"
}
```

**Get Cached KYC:**
```bash
GET /api/agents/kyc?pan=GOODPAN123
```

---

## 3️⃣ **Credit Check API**

**Endpoint:** `POST /api/agents/credit`

**File:** `loan-agent-system/app/api/agents/credit/route.ts`

**Purpose:** Fetch credit score and credit history

**Request Body:**
```json
{
  "pan": "GOODPAN123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "score": 790,
    "status": "No defaults",
    "active_loans": 1,
    "credit_history_years": 8
  },
  "message": "✅ Credit Score: 790 (Very Good)\n\n📊 Credit Assessment:...",
  "meetsMinimumRequirement": true
}
```

**Health Check:**
```bash
GET /api/agents/credit/health
```

---

## 4️⃣ **Underwriting API**

**Endpoint:** `POST /api/agents/underwriting`

**File:** `loan-agent-system/app/api/agents/underwriting/route.ts`

**Purpose:** Evaluate loan application and make approval decision

**Request Body:**
```json
{
  "loanData": {
    "pan_number": "GOODPAN123",
    "full_name": "Rohan Gupta",
    "age": 35,
    "phone": "9876543210",
    "employment_type": "Salaried",
    "monthly_income": 75000,
    "company_name": "TCS",
    "loan_amount_requested": 500000,
    "loan_purpose": "Wedding",
    "preferred_tenure": 36,
    "existing_emi": 12000,
    "credit_score": 790,
    "credit_status": "No defaults",
    "active_loans": 1
  },
  "userId": "user-uuid-here"
}
```

**Response (Approved):**
```json
{
  "success": true,
  "decision": "approved",
  "data": {
    "approved": true,
    "sanctioned_amount": 500000,
    "interest_rate": 11.5,
    "monthly_emi": 16680,
    "tenure": 36,
    "dti_ratio": 38.24
  },
  "message": "🎉 Congratulations Rohan Gupta! Your loan has been APPROVED!...",
  "applicationId": "uuid-of-application",
  "counterOffer": null
}
```

**Response (Rejected):**
```json
{
  "success": true,
  "decision": "rejected",
  "data": {
    "approved": false,
    "rejection_reason": "Application does not meet eligibility criteria",
    "failed_rules": [
      "Minimum credit score required: 650",
      "Debt-to-Income ratio (55.0%) exceeds maximum allowed (50%)"
    ]
  },
  "message": "❌ Sorry, we're unable to approve your loan application...",
  "applicationId": "uuid-of-application",
  "counterOffer": {
    "amount": 300000,
    "message": "We can offer up to ₹3,00,000 instead."
  }
}
```

**Get Application:**
```bash
GET /api/agents/underwriting/application?id=<application-id>
```

---

## 5️⃣ **Document Generation API**

**Endpoint:** `POST /api/agents/document`

**File:** `loan-agent-system/app/api/agents/document/route.ts`

**Purpose:** Generate PDF sanction letter

**Request Body:**
```json
{
  "applicationId": "APP2025001234",
  "customerName": "Rohan Gupta",
  "panNumber": "GOODPAN123",
  "phone": "9876543210",
  "sanctionedAmount": 500000,
  "interestRate": 11.5,
  "tenure": 36,
  "monthlyEmi": 16680
}
```

**Response:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="Sanction_Letter_APP2025001234_Rohan_Gupta_1234567890.pdf"

[PDF Binary Data]
```

**Health Check:**
```bash
GET /api/agents/document/health
```

---

## 🧪 **Testing the APIs**

### **Using curl:**

#### Test Chat API:
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want a loan",
    "conversationState": {
      "stage": "greeting",
      "loan_data": {},
      "messages": [],
      "kyc_verified": false,
      "credit_checked": false
    }
  }'
```

#### Test KYC API:
```bash
curl -X POST http://localhost:3000/api/agents/kyc \
  -H "Content-Type: application/json" \
  -d '{"pan": "GOODPAN123"}'
```

#### Test Credit API:
```bash
curl -X POST http://localhost:3000/api/agents/credit \
  -H "Content-Type: application/json" \
  -d '{"pan": "GOODPAN123"}'
```

#### Test Document API:
```bash
curl -X POST http://localhost:3000/api/agents/document \
  -H "Content-Type: application/json" \
  -d '{
    "applicationId": "TEST123",
    "customerName": "Rohan Gupta",
    "panNumber": "GOODPAN123",
    "phone": "9876543210",
    "sanctionedAmount": 500000,
    "interestRate": 11.5,
    "tenure": 36,
    "monthlyEmi": 16680
  }' \
  --output sanction-letter.pdf
```

### **Using Postman:**

1. Create a new request
2. Set method to POST
3. Set URL to `http://localhost:3000/api/chat`
4. Go to Body → raw → JSON
5. Paste the request body
6. Click Send

---

## 🔒 **Authentication**

Currently, the APIs work without authentication for testing. To add authentication:

1. **Add middleware check:**
```typescript
import { createClient } from '@/lib/supabase/server';

const supabase = await createClient();
const { data: { user } } = await supabase.auth.getUser();

if (!user) {
  return NextResponse.json(
    { error: 'Unauthorized' },
    { status: 401 }
  );
}
```

2. **Pass authentication token in headers:**
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 📊 **API Flow**

Here's the typical flow of API calls:

```
1. User starts chat
   POST /api/chat
   → Response: "Please provide your PAN"

2. User provides PAN
   POST /api/chat
   → Internally calls KYC verification
   → Response: "PAN verified! What's your employment type?"

3. User provides employment details
   POST /api/chat
   → Response: "What's your monthly income?"

4. Continue until all data collected
   POST /api/chat (multiple times)

5. When ready, make underwriting decision
   POST /api/agents/underwriting
   → Response: Approved/Rejected

6. If approved, generate sanction letter
   POST /api/agents/document
   → Response: PDF file
```

---

## 🐛 **Error Codes**

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request (missing/invalid data) |
| 401 | Unauthorized (not logged in) |
| 404 | Not Found (resource doesn't exist) |
| 500 | Internal Server Error |

---

## 📝 **Common Errors**

### Error: "Message is required"
**Cause:** Missing `message` field in request body
**Fix:** Include `message` in POST body

### Error: "Conversation state is required"
**Cause:** Missing `conversationState` field
**Fix:** Include valid conversation state object

### Error: "PAN not found"
**Cause:** PAN doesn't exist in mock database
**Fix:** Use one of these test PANs:
- GOODPAN123
- ABCDE1234F
- FGHIJ5678K
- BADPAN456

### Error: "Failed to generate sanction letter"
**Cause:** Missing required fields for PDF generation
**Fix:** Ensure all required fields are included in request

---

## ✅ **Health Check All Services**

```bash
# Chat API
curl http://localhost:3000/api/chat

# Credit API
curl http://localhost:3000/api/agents/credit/health

# Document API
curl http://localhost:3000/api/agents/document/health
```

---

## 📦 **File Structure**

```
loan-agent-system/app/api/
├── chat/
│   └── route.ts              ✅ Main chat endpoint
└── agents/
    ├── kyc/
    │   └── route.ts          ✅ KYC verification
    ├── credit/
    │   └── route.ts          ✅ Credit check
    ├── underwriting/
    │   └── route.ts          ✅ Underwriting decision
    └── document/
        └── route.ts          ✅ PDF generation
```

---

## 🎯 **Next Steps**

1. ✅ All API routes created
2. ⏳ Create frontend chat UI
3. ⏳ Create authentication pages
4. ⏳ Test end-to-end flow
5. ⏳ Deploy to production

---

**All API routes are ready to use! Start the dev server and test them:**

```bash
npm run dev
```

Then visit: `http://localhost:3000/api/chat`