-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Loan Applications Table
CREATE TABLE loan_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- KYC Data
    pan_number VARCHAR(10),
    full_name VARCHAR(100),
    age INTEGER,
    phone VARCHAR(10),
    
    -- Employment
    employment_type VARCHAR(20),
    monthly_income DECIMAL(12,2),
    company_name VARCHAR(100),
    
    -- Loan Details
    loan_amount_requested DECIMAL(12,2),
    loan_purpose VARCHAR(50),
    preferred_tenure INTEGER,
    
    -- Existing Obligations
    existing_emi DECIMAL(10,2) DEFAULT 0,
    has_credit_card BOOLEAN DEFAULT FALSE,
    credit_card_outstanding DECIMAL(10,2) DEFAULT 0,
    
    -- Credit Data
    credit_score INTEGER,
    credit_status VARCHAR(100),
    active_loans INTEGER DEFAULT 0,
    
    -- Decision
    approval_status VARCHAR(20) DEFAULT 'pending',
    sanctioned_amount DECIMAL(12,2),
    interest_rate DECIMAL(5,2),
    monthly_emi DECIMAL(10,2),
    rejection_reason TEXT,
    failed_rules TEXT[],
    
    -- Documents
    sanction_letter_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversation Logs Table
CREATE TABLE conversation_logs (
    id SERIAL PRIMARY KEY,
    application_id UUID REFERENCES loan_applications(id) ON DELETE CASCADE,
    sender VARCHAR(20) CHECK (sender IN ('user', 'agent')),
    message TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_loan_app_user ON loan_applications(user_id);
CREATE INDEX idx_loan_app_status ON loan_applications(approval_status);
CREATE INDEX idx_conv_logs_app ON conversation_logs(application_id);

-- Enable RLS (Row Level Security)
ALTER TABLE loan_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own applications" 
    ON loan_applications FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own applications" 
    ON loan_applications FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own applications" 
    ON loan_applications FOR UPDATE 
    USING (auth.uid() = user_id);
