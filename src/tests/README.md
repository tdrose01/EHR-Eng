# EHR Vue App Testing Guide

This directory contains tests for the EHR Vue App. There are two types of tests:

1. **Unit Tests**: Test individual components in isolation with mocked dependencies
2. **End-to-End Tests**: Test components with a simulated API backend

## Test Structure

```
tests/
├── e2e/                    # End-to-end tests with simulated API
│   ├── setup.js            # Setup file for E2E tests (MSW server and test data)
│   └── *.e2e.spec.js       # E2E test files
├── views/                  # Unit tests for view components
│   └── *.spec.js           # Unit test files
└── README.md               # This file
```

## Running Tests

### Unit Tests

These tests validate individual components in isolation:

```bash
# Run all unit tests
npm test

# Run unit tests in watch mode
npm run test:watch

# Run with coverage report
npm run test:coverage
```

### End-to-End Tests

These tests use Mock Service Worker (MSW) to simulate API endpoints and test components with real data flow:

```bash
# Run all end-to-end tests
npm run test:e2e

# Run end-to-end tests in watch mode
npm run test:e2e:watch
```

## Writing Tests

### Unit Tests

Unit tests should focus on testing a single component in isolation:

```javascript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent.vue', () => {
  it('renders correctly', () => {
    const wrapper = mount(MyComponent)
    expect(wrapper.text()).toContain('Expected content')
  })
})
```

### End-to-End Tests

End-to-end tests should use the setup in `e2e/setup.js` to test components with the simulated API:

```javascript
import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'
import { testDb } from './setup'

describe('MyComponent E2E', () => {
  it('loads data from API correctly', async () => {
    const wrapper = mount(MyComponent)
    await flushPromises() // Wait for API calls
    
    // Check component state after API call
    expect(wrapper.text()).toContain(testDb.patients[0].firstName)
  })
})
```

## Test Data

Test data is defined in `e2e/setup.js` in the `testDb` object. You can modify this data to test different scenarios.

## Mocking API Responses

The Mock Service Worker intercepts API calls and returns responses based on the test data. If you need to mock additional API endpoints, add them to the `handlers` array in `e2e/setup.js`. 