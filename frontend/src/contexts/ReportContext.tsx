/**
 * Report Context
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { apiClient } from '../services/api';
import type { ReportFilter, FilterOptions, ReportData, UniverSnapshot } from '../types';

interface ReportContextType {
  filterOptions: FilterOptions | null;
  currentFilter: ReportFilter | null;
  reportData: ReportData | null;
  univerSnapshot: UniverSnapshot | null;
  isLoading: boolean;
  error: string | null;
  loadFilterOptions: () => Promise<void>;
  generateReport: (filter: ReportFilter) => Promise<void>;
  generateUniverSnapshot: (filter: ReportFilter) => Promise<void>;
  setCurrentFilter: (filter: ReportFilter) => void;
  clearError: () => void;
  clearReport: () => void;
}

const ReportContext = createContext<ReportContextType | undefined>(undefined);

export const useReport = () => {
  const context = useContext(ReportContext);
  if (!context) {
    throw new Error('useReport must be used within ReportProvider');
  }
  return context;
};

interface ReportProviderProps {
  children: ReactNode;
}

export const ReportProvider: React.FC<ReportProviderProps> = ({ children }) => {
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [currentFilter, setCurrentFilter] = useState<ReportFilter | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [univerSnapshot, setUniverSnapshot] = useState<UniverSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadFilterOptions = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const options = await apiClient.getFilterOptions();
      setFilterOptions(options);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || 'Failed to load filter options.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const generateReport = async (filter: ReportFilter) => {
    setIsLoading(true);
    setError(null);
    setCurrentFilter(filter);

    try {
      const data = await apiClient.generateReport(filter);
      setReportData(data);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || 'Failed to generate report.';
      setError(errorMessage);
      setReportData(null);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const generateUniverSnapshot = async (filter: ReportFilter) => {
    setIsLoading(true);
    setError(null);
    setCurrentFilter(filter);

    try {
      const snapshot = await apiClient.generateUniverSnapshot(filter);
      setUniverSnapshot(snapshot);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || 'Failed to generate Univer snapshot.';
      setError(errorMessage);
      setUniverSnapshot(null);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const clearReport = () => {
    setReportData(null);
    setUniverSnapshot(null);
    setCurrentFilter(null);
  };

  const value: ReportContextType = {
    filterOptions,
    currentFilter,
    reportData,
    univerSnapshot,
    isLoading,
    error,
    loadFilterOptions,
    generateReport,
    generateUniverSnapshot,
    setCurrentFilter,
    clearError,
    clearReport,
  };

  return <ReportContext.Provider value={value}>{children}</ReportContext.Provider>;
};
