export type UserRole = 'CONSIDERER' | 'BUYER' | 'ADMIN';
export type CampaignStatus = 'DRAFT' | 'ACTIVE' | 'PAUSED' | 'COMPLETED' | 'CANCELLED';
export type ProofStatus = 'PENDING' | 'PROCESSING' | 'VERIFIED' | 'REJECTED' | 'DISPUTED';
export type PaymentStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'REFUNDED';

export interface VerificationScores {
  relevanceScore: number;
  noveltyScore: number;
  coherenceScore: number;
  effortScore: number;
  aiDetectionScore: number;
  combinedScore: number;
}

export interface VerificationResult extends VerificationScores {
  passed: boolean;
  feedback: string;
  processingTimeMs: number;
}

export interface ProofMetadata {
  timeSpentSeconds: number;
  revisionCount: number;
  startedAt: string;
}

export interface CampaignAnalytics {
  totalResponses: number;
  verifiedResponses: number;
  averageScore: number;
  budgetSpent: number;
  budgetRemaining: number;
}
