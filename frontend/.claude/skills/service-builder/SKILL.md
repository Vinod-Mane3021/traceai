---
name: service-builder
description: Build pure, interface-agnostic services with injected dependencies. Use when creating business logic that must work across API hooks, CLI commands, or tests. Invoke with /service-builder.
---

# Service Builder

You are an expert at building pure, testable services that are decoupled from their callers in Trace.ai.

## North Star

**Every service is decoupled from its interface (I/O).** A service takes plain data in, does work, and returns plain data out. In the Trace.ai frontend, services encapsulate business logic and data transformations, keeping the UI components and TanStack Query hooks thin.

## Workflow

When asked to create a service, follow these steps:

### Step 1: Define the Contract

Start with the input/output types in `src/types/`.

```typescript
// src/types/rule.ts
export interface CustomRule {
  id: string;
  name: string;
  repository_id: number;
}

export interface CreateRuleInput {
  name: string;
  repository_id: number;
}
```

### Step 2: Build the Service

The service receives dependencies (like the API requester) through its constructor or as arguments. It should not directly depend on global state or environment variables if possible.

Create in `src/features/[feature]/lib/[feature].service.ts`.

```typescript
// src/features/rules/lib/rule.service.ts
import { CustomRule, CreateRuleInput } from "@/types/rule";

export type ApiRequester = <T>(path: string, init?: RequestInit) => Promise<T>;

export function createRuleService(apiRequest: ApiRequester) {
  return new RuleService(apiRequest);
}

class RuleService {
  constructor(private readonly apiRequest: ApiRequester) {}

  async createRule(input: CreateRuleInput): Promise<CustomRule> {
    // Business logic: validation or transformation
    if (input.name.length < 3) {
      throw new Error("Rule name must be at least 3 characters");
    }

    return this.apiRequest<CustomRule>("/v1/rules/", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  async validateRuleLogic(logic: string): Promise<boolean> {
    // Pure logic or complex calculation
    return logic.includes("trigger");
  }
}
```

### Step 3: Integrate with API Hooks

The API hook is a thin adapter that resolves dependencies (like `apiRequest`) and calls the service.

```typescript
// src/features/rules/api/use-create-rule.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { createRuleService } from "../lib/rule.service";

export function useCreateRule() {
  const qc = useQueryClient();
  const service = createRuleService(apiRequest);

  return useMutation({
    mutationFn: (input) => service.createRule(input),
    onSuccess: (rule) => {
      qc.invalidateQueries({ queryKey: ["rules", rule.repository_id] });
    },
  });
}
```

### Step 4: Write Tests

Because the service accepts dependencies, you can test it with mocks without a running backend.

```typescript
// src/features/rules/lib/__tests__/rule.service.test.ts
import { describe, it, expect, vi } from 'vitest';
import { createRuleService } from '../rule.service';

describe('RuleService', () => {
  it('validates rule name length', async () => {
    const mockApi = vi.fn();
    const service = createRuleService(mockApi);

    await expect(service.createRule({ name: 'ab', repository_id: 1 }))
      .rejects.toThrow("Rule name must be at least 3 characters");
  });

  it('calls API with correct params', async () => {
    const mockApi = vi.fn().mockResolvedValue({ id: '1', name: 'Valid' });
    const service = createRuleService(mockApi);

    await service.createRule({ name: 'Valid Name', repository_id: 1 });
    
    expect(mockApi).toHaveBeenCalledWith("/v1/rules/", expect.objectContaining({
      method: "POST"
    }));
  });
});
```

## Rules

1. **Services are pure functions or classes over data.** Plain objects in, plain objects out.
2. **Inject dependencies.** The service receives its API requester or any I/O capability. Never call `env` directly inside a service if it can be passed in.
3. **API hooks are trivial glue.** A hook resolves `apiRequest`, calls the service, and handles cache invalidation.
4. **Testable in isolation.** Pass a mock requester, assert the output.

## File Structure

```
src/features/feature/
├── api/
│   └── use-feature.ts       # TanStack Query hooks
└── lib/
    ├── feature.service.ts   # Core logic
    ├── feature.schema.ts    # Zod schemas
    └── mock-feature.ts      # Mock data for env.mockApi
```

## Anti-Patterns

- **❌ BAD**: Service imports `apiRequest` directly (coupling).
- **❌ BAD**: Business logic directly in the `useMutation` hook.
- **❌ BAD**: Two hooks duplicating the same data transformation logic.
- **❌ BAD**: Service accessing `useAuthStore` directly (should be passed as a param or handled in the hook).
