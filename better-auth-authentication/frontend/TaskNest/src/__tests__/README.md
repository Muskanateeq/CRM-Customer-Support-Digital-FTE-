# Frontend Tests

This directory contains automated tests for the TaskNest frontend application.

## Test Structure

- `components/tasks/__tests__/` - Task component tests
  - `TaskForm.test.tsx` - Task creation/editing form tests
  - `TaskItem.test.tsx` - Individual task display tests
- `hooks/__tests__/` - Custom hook tests
  - `useTasks.test.ts` - Task management hook tests
- `lib/__tests__/` - Utility and API tests
  - `api.test.ts` - API client tests

## Running Tests

```bash
# Install dependencies
cd frontend/TaskNest
npm install

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- TaskForm.test.tsx

# Run specific test
npm test -- -t "renders create form with empty fields"
```

## Test Coverage

- ✅ TaskForm component (create/edit modes)
- ✅ TaskItem component (display and interactions)
- ✅ useTasks hook (CRUD operations, filtering, searching)
- ✅ API client (all endpoints, error handling, authentication)
- ✅ Form validation
- ✅ User interactions
- ✅ Error states
- ✅ Loading states

## Writing New Tests

### Component Test Example

```typescript
import { render, screen } from '@testing-library/react';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### Hook Test Example

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useMyHook } from '../useMyHook';

describe('useMyHook', () => {
  it('returns expected value', async () => {
    const { result } = renderHook(() => useMyHook());

    await waitFor(() => {
      expect(result.current.value).toBe('expected');
    });
  });
});
```

## Mocking

- API calls are mocked using `jest.mock('@/lib/api')`
- Browser APIs (localStorage, Notification) are mocked in `jest.setup.js`
- Next.js router is mocked when needed

## Best Practices

1. Test user behavior, not implementation details
2. Use `screen.getByRole()` for accessibility
3. Use `waitFor()` for async operations
4. Mock external dependencies
5. Keep tests focused and isolated
6. Use descriptive test names
