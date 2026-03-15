/**
 * Jest Setup File
 *
 * Runs before each test file.
 */

import '@testing-library/jest-dom';

// Mock better-auth module
jest.mock('better-auth/react', () => ({
  createAuthClient: jest.fn(() => ({
    useSession: jest.fn(() => ({
      data: { session: { userId: 'test-user-id' }, user: { id: 'test-user-id', email: 'test@example.com' } },
      isPending: false,
      error: null,
    })),
    signIn: {
      email: jest.fn(),
      social: jest.fn(),
    },
    signOut: jest.fn(),
    signUp: {
      email: jest.fn(),
    },
  })),
}));

// Mock auth-client
jest.mock('@/lib/auth-client', () => ({
  authClient: {
    useSession: jest.fn(() => ({
      data: { session: { userId: 'test-user-id' }, user: { id: 'test-user-id', email: 'test@example.com' } },
      isPending: false,
      error: null,
    })),
    signIn: {
      email: jest.fn(),
      social: jest.fn(),
    },
    signOut: jest.fn(),
    signUp: {
      email: jest.fn(),
    },
  },
  getJWTToken: jest.fn(() => Promise.resolve('mock-jwt-token')),
  getAuthHeader: jest.fn(() => Promise.resolve({ Authorization: 'Bearer mock-jwt-token' })),
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};

// Mock Notification API
global.Notification = {
  permission: 'default',
  requestPermission: jest.fn(() => Promise.resolve('granted')),
};

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;
