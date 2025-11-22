import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { ReportProvider, useReport } from '../ReportContext'
import { ReactNode } from 'react'

// Mock API client
vi.mock('../../services/api', () => ({
  default: {
    getFilterOptions: vi.fn(),
    generateReport: vi.fn(),
    generateUniverSnapshot: vi.fn(),
    exportToExcel: vi.fn(),
    reloadData: vi.fn(),
  },
}))

describe('ReportContext', () => {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <ReportProvider>{children}</ReportProvider>
  )

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should provide initial report state', () => {
    const { result } = renderHook(() => useReport(), { wrapper })

    expect(result.current.filterOptions).toBeNull()
    expect(result.current.reportData).toBeNull()
    expect(result.current.univerSnapshot).toBeNull()
    expect(result.current.currentFilter).toBeNull()
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('should have report methods', () => {
    const { result } = renderHook(() => useReport(), { wrapper })

    expect(typeof result.current.loadFilterOptions).toBe('function')
    expect(typeof result.current.generateReport).toBe('function')
    expect(typeof result.current.exportReport).toBe('function')
    expect(typeof result.current.reloadData).toBe('function')
    expect(typeof result.current.clearError).toBe('function')
  })
})
