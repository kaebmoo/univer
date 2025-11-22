/**
 * TypeScript Type Definitions
 */

// Auth Types
export interface OTPRequest {
  email: string;
}

export interface OTPVerifyRequest {
  email: string;
  otp_code: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserInfo {
  email: string;
  domain: string;
}

// Report Types
export interface ReportFilter {
  year: number;
  months: number[];
  business_groups?: string[] | null;
}

export interface FilterOptions {
  available_years: number[];
  available_business_groups: string[];
  available_services: string[];
  min_date: string;
  max_date: string;
}

export interface ReportMetrics {
  total_revenue: number;
  total_cost_of_service: number;
  total_selling_cost: number;
  total_support_cost: number;
  total_cost: number;
  ebit: number;
  ebitda: number;
  gross_profit: number;
  gross_profit_margin: number;
  ebit_margin: number;
  ebitda_margin: number;
}

export interface ReportData {
  metadata: {
    year: number;
    months: number[];
    business_groups: string[] | string;
    view_type: string;
    display_type: string;
    show_common_size: boolean;
    generated_at: string;
  };
  data: {
    revenue: Record<string, number>;
    cost_of_service: Record<string, number>;
    selling_expense: Record<string, number>;
    admin_expense: Record<string, number>;
    metrics: ReportMetrics;
    common_size?: {
      revenue: Record<string, number>;
      cost_of_service: Record<string, number>;
    };
  };
}

// Univer Types
export interface UniverSnapshot {
  id: string;
  name: string;
  appVersion: string;
  locale: string;
  styles: Record<string, any>;
  sheets: Record<string, UniverSheet>;
}

export interface UniverSheet {
  id: string;
  name: string;
  cellData: Record<number, Record<number, UniverCell>>;
  rowCount: number;
  columnCount: number;
  defaultRowHeight?: number;
  defaultColumnWidth?: number;
}

export interface UniverCell {
  v: any;
  t?: string;
  s?: string;
  f?: string;
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  details?: any;
}
