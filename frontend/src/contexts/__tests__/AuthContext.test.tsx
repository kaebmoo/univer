import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../AuthContext'
import { ReactNode } from 'react'

// Mock API client
vi.mock('../../services/api', () => ({
  default: {
    isAuthenticated: vi.fn(() => false),
    getCurrentUser: vi.fn(),
    requestOTP: vi.fn(),
    verifyOTP: vi.fn(),
    clearToken: vi.fn(),
    setToken: vi.fn(),
  },
}))

describe('AuthContext', () => {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  )

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should provide initial auth state', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.user).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('should have auth methods', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(typeof result.current.requestOTP).toBe('function')
    expect(typeof result.current.verifyOTP).toBe('function')
    expect(typeof result.current.logout).toBe('function')
    expect(typeof result.current.clearError).toBe('function')
  })

  it('should clear error', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Simulate error (in real usage this would come from API call)
    // For now just check clearError exists
    result.current.clearError()
    expect(result.current.error).toBeNull()
  })
})
