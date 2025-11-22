/**
 * API Client Service
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  OTPRequest,
  OTPVerifyRequest,
  TokenResponse,
  UserInfo,
  FilterOptions,
  ReportFilter,
  ReportData,
  UniverSnapshot,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage
    this.token = localStorage.getItem('access_token');
    if (this.token) {
      this.setAuthToken(this.token);
    }

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearAuth();
          window.location.href = '/';
        }
        return Promise.reject(error);
      }
    );
  }

  private setAuthToken(token: string) {
    this.token = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('access_token', token);
  }

  private clearAuth() {
    this.token = null;
    delete this.client.defaults.headers.common['Authorization'];
    localStorage.removeItem('access_token');
  }

  // ===== Authentication API =====

  async requestOTP(data: OTPRequest): Promise<{ message: string; email: string; expires_in: number }> {
    const response = await this.client.post('/auth/request-otp', data);
    return response.data;
  }

  async verifyOTP(data: OTPVerifyRequest): Promise<TokenResponse> {
    const response = await this.client.post('/auth/verify-otp', data);
    const tokenData = response.data;

    // Save token
    this.setAuthToken(tokenData.access_token);

    return tokenData;
  }

  async getCurrentUser(): Promise<UserInfo> {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.clearAuth();
    }
  }

  // ===== Report API =====

  async getFilterOptions(): Promise<FilterOptions> {
    const response = await this.client.get('/report/filters');
    return response.data;
  }

  async generateReport(filter: ReportFilter): Promise<ReportData> {
    const response = await this.client.post('/report/generate', filter);
    return response.data;
  }

  async generateUniverSnapshot(filter: ReportFilter): Promise<UniverSnapshot> {
    const response = await this.client.post('/report/univer', filter);
    return response.data;
  }

  async reloadData(): Promise<any> {
    const response = await this.client.post('/report/reload-data');
    return response.data;
  }

  // ===== Health Check =====

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ===== Helper Methods =====

  isAuthenticated(): boolean {
    return this.token !== null;
  }

  getToken(): string | null {
    return this.token;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
