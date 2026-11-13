export interface Transaction {
  id: string;
  cardNumber: string;
  accountId: string;
  amountClp: number;
  currency: string;
  mcc: string;
  merchantName: string;
  channel: string;
  city: string;
  country: string;
  timestamp: string;
  isSuspicious: boolean;
}

export interface RiskScore {
  score: number;
  riskLevel: 'NORMAL' | 'REVISAR' | 'AUTOFRAUDE_PROBABLE';
  confidence: number;
  triggeredRules: string[];
  recommendedAction: string;
  mlPrediction?: MLPrediction;
}

export interface MLPrediction {
  experimentalScore: number;
  modelVersion: string;
  modelScope: 'synthetic' | 'approved_labeled' | string;
  probabilityCalibrated: boolean;
  reasonCodes: string[];
}

export interface Alert {
  id: string;
  transactionId: string;
  cardNumber: string;
  amountClp: number;
  merchantName: string;
  riskScore: RiskScore;
  status: 'PENDIENTE' | 'CONGELADO_PREVENTIVO' | 'REVERTIDO' | 'FRAUDE_CONFIRMADO';
  createdAt: string;
  actionTakenBy?: string;
  actionTimestamp?: string;
}

export interface SystemStats {
  totalProcessed: number;
  totalAlerts: number;
  activeFreezes: number;
  preventedLossClp: number;
  averageLatencyMs: number;
  autopoiesisCycle: number;
}
