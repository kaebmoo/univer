import { describe, it, expect, beforeEach, vi } from 'vitest'
import type { Mock } from 'vitest'
import apiClient from '../api'
import type { ReportFilter } from '../../types'

// Mock axios
vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
        get: vi.fn(),
        post: vi.fn(),
      })),
    },
  }
})

describe('APIClient', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('should check if authenticated', () => {
    // No token - should be false
    expect(apiClient.isAuthenticated()).toBe(false)

    // With token - should be true
    localStorage.setItem('auth_token', 'test-token')
    expect(apiClient.isAuthenticated()).toBe(true)
  })

  it('should get token from localStorage', () => {
    const testToken = 'test-token-123'
    localStorage.setItem('auth_token', testToken)

    expect(apiClient.getToken()).toBe(testToken)
  })

  it('should set token in localStorage', () => {
    const testToken = 'new-token-456'
    apiClient.setToken(testToken)

    expect(localStorage.getItem('auth_token')).toBe(testToken)
  })

  it('should clear token from localStorage', () => {
    localStorage.setItem('auth_token', 'some-token')
    apiClient.clearToken()

    expect(localStorage.getItem('auth_token')).toBeNull()
  })
})

describe('API Methods Type Checking', () => {
  it('should have correct method signatures', () => {
    expect(typeof apiClient.requestOTP).toBe('function')
    expect(typeof apiClient.verifyOTP).toBe('function')
    expect(typeof apiClient.getCurrentUser).toBe('function')
    expect(typeof apiClient.getFilterOptions).toBe('function')
    expect(typeof apiClient.generateReport).toBe('function')
    expect(typeof apiClient.generateUniverSnapshot).toBe('function')
    expect(typeof apiClient.exportToExcel).toBe('function')
    expect(typeof apiClient.reloadData).toBe('function')
  })
})
