# Server Function Examples (TanStack Start)

## Authenticated Server Function

```typescript
import { createServerFn } from "@tanstack/react-start";
import { getAuthToken } from "@/features/auth/store/auth-store"; // Note: In server functions, you might need a different way to get the session if not passed in.

export const getSecureData = createServerFn("GET", async () => {
  // Logic to check session on server
  // ...
  
  return { data: "secure info" };
});
```

## Mutation with Service

```typescript
import { createServerFn } from "@tanstack/react-start";
import { CreateRuleSchema } from "../lib/rule.schema";
import { createRuleService } from "../lib/rule.service";
import { apiRequest } from "@/lib/fetch-api";

export const createRuleFn = createServerFn("POST", async (payload) => {
  const data = CreateRuleSchema.parse(payload);
  const service = createRuleService(apiRequest);
  
  return await service.createRule(data);
});
```

## Server Function used with TanStack Query

```typescript
// src/features/rules/api/use-rules.ts
import { useQuery } from "@tanstack/react-query";
import { createServerFn } from "@tanstack/react-start";

const fetchRulesFn = createServerFn("GET", async (repositoryId: string) => {
  // Call backend API
  // return apiRequest(...)
});

export function useRules(repositoryId: string) {
  return useQuery({
    queryKey: ["rules", repositoryId],
    queryFn: () => fetchRulesFn(repositoryId),
  });
}
```
