// ============================================================================
// MOCK KYC DATABASE - Simulates government KYC verification service
// ============================================================================

export interface MockKYCRecord {
  pan_number: string;
  full_name: string;
  date_of_birth: string;
  kyc_status: 'VERIFIED' | 'PENDING_AADHAAR_LINK' | 'BLOCKED';
  phone: string;
  address?: string;
}

export const MOCK_KYC_DATABASE: Record<string, MockKYCRecord> = {
  // ========== Good Credit Profiles ==========
  "GOODPAN123": {
    pan_number: "GOODPAN123",
    full_name: "Rohan Gupta",
    date_of_birth: "1990-05-15",
    kyc_status: "VERIFIED",
    phone: "9876543210",
    address: "Mumbai, Maharashtra"
  },
  
  "ABCDE1234F": {
    pan_number: "ABCDE1234F",
    full_name: "Rajesh Kumar",
    date_of_birth: "1988-03-20",
    kyc_status: "VERIFIED",
    phone: "9876543211",
    address: "Bangalore, Karnataka"
  },
  
  "FGHIJ5678K": {
    pan_number: "FGHIJ5678K",
    full_name: "Priya Sharma",
    date_of_birth: "1992-11-08",
    kyc_status: "VERIFIED",
    phone: "9876543212",
    address: "Delhi, NCR"
  },
  
  // ========== Average Credit Profiles ==========
  "BADPAN456": {
    pan_number: "BADPAN456",
    full_name: "Priya Singh",
    date_of_birth: "1995-11-20",
    kyc_status: "VERIFIED",
    phone: "9876543213",
    address: "Pune, Maharashtra"
  },
  
  "KLMNO9012P": {
    pan_number: "KLMNO9012P",
    full_name: "Amit Sharma",
    date_of_birth: "1985-07-12",
    kyc_status: "VERIFIED",
    phone: "9876543214",
    address: "Hyderabad, Telangana"
  },
  
  // ========== KYC Issues ==========
  "KYCFAIL789": {
    pan_number: "KYCFAIL789",
    full_name: "Amit Verma",
    date_of_birth: "1988-01-30",
    kyc_status: "PENDING_AADHAAR_LINK",
    phone: "9876543215",
    address: "Chennai, Tamil Nadu"
  },
  
  // ========== Additional Test Profiles ==========
  "PQRST3456U": {
    pan_number: "PQRST3456U",
    full_name: "Sneha Reddy",
    date_of_birth: "1993-09-25",
    kyc_status: "VERIFIED",
    phone: "9876543216",
    address: "Kochi, Kerala"
  },
  
  "UVWXY7890Z": {
    pan_number: "UVWXY7890Z",
    full_name: "Vikas Patel",
    date_of_birth: "1987-02-14",
    kyc_status: "VERIFIED",
    phone: "9876543217",
    address: "Ahmedabad, Gujarat"
  },
  
  "AAAAA1111A": {
    pan_number: "AAAAA1111A",
    full_name: "Ananya Iyer",
    date_of_birth: "1991-06-30",
    kyc_status: "VERIFIED",
    phone: "9876543218",
    address: "Kolkata, West Bengal"
  },
  
  "BBBBB2222B": {
    pan_number: "BBBBB2222B",
    full_name: "Rahul Mehta",
    date_of_birth: "1994-12-05",
    kyc_status: "VERIFIED",
    phone: "9876543219",
    address: "Jaipur, Rajasthan"
  }
};

/**
 * Simulate KYC verification with realistic delay
 */
export async function verifyKYC(pan: string): Promise<MockKYCRecord | null> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const record = MOCK_KYC_DATABASE[pan.toUpperCase()];
  return record || null;
}

/**
 * Calculate age from date of birth
 */
export function calculateAge(dob: string): number {
  const today = new Date();
  const birthDate = new Date(dob);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age;
}