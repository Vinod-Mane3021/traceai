---
name: server-function-builder
description: Create TanStack Start Server Functions with createServerFn, Zod validation, and service patterns. Use when implementing server-side logic, database interactions, or API operations that need to run on the server. Invoke with /server-function-builder.
---

# Server Function Builder

You are an expert at creating type-safe server functions for Trace.ai using TanStack Start.

## Workflow

When asked to create a server function, follow these steps:

### Step 1: Create Zod Schema

Create validation schema in `src/features/[feature]/lib/[feature].schema.ts`:

```typescript
import { z } from 'zod';

export const CreateItemSchema = z.object({
  name: z.string().min(1, 'Name is required'),
});

export type CreateItemInput = z.infer<typeof CreateItemSchema>;
```

### Step 2: Create Service Layer

The service contains the pure logic. It should not depend on TanStack Start specifics.

Create in `src/features/[feature]/lib/[feature].service.ts`.

### Step 3: Create Server Function (Thin Adapter)

The server function is a **thin adapter** that resolves dependencies and delegates to the service.

Create in `src/features/[feature]/api/server-functions.ts`:

```typescript
import { createServerFn } from "@tanstack/react-start";
import { CreateItemSchema } from "../lib/item.schema";
import { createItemService } from "../lib/item.service";
import { apiRequest } from "@/lib/fetch-api";

export const createItemFn = createServerFn("POST", async (input: CreateItemInput) => {
  // Validate input
  const data = CreateItemSchema.parse(input);
  
  // Resolve service (inject dependencies)
  const service = createItemService(apiRequest);
  
  // Call service
  const result = await service.createItem(data);
  
  return result;
});
```

### Step 4: Use in Client Hook

Wrap the server function in a TanStack Query hook for easy usage in components.

```typescript
// src/features/feature/api/use-create-item.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createItemFn } from "./server-functions";

export function useCreateItem() {
  const qc = useQueryClient();
  
  return useMutation({
    mutationFn: createItemFn,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["items"] });
    },
  });
}
```

## Key Patterns

1. **Services are pure, adapters are thin.** Keep business logic in services.
2. **Inject dependencies.** Pass the requester or other I/O capabilities to the service.
3. **Validation.** Use Zod to validate inputs at the server function boundary.
4. **Error Handling.** Let errors bubble up or catch them to provide user-friendly messages.

## File Structure

```
src/features/feature/
├── api/
│   ├── server-functions.ts    # TanStack Start server functions
│   └── use-create-item.ts     # Client-side mutation hook
└── lib/
    ├── feature.service.ts     # Core logic
    └── feature.schema.ts      # Zod schemas
```
