# Server Function Reference (TanStack Start)

## createServerFn API

```typescript
import { createServerFn } from "@tanstack/react-start";

export const myFn = createServerFn(method, handler);
```

- `method`: "GET" | "POST"
- `handler`: Async function that runs on the server.

### Usage in Client

```typescript
const result = await myFn(payload);
```

## Context & Middleware

In TanStack Start, you can use middleware to inject context (like auth) into server functions.

```typescript
// Example middleware pattern (if implemented in project)
import { createServerFn } from "@tanstack/react-start";

export const secureFn = createServerFn("POST", async (data, ctx) => {
  // ctx might contain user info from middleware
});
```

## Error Handling

Server functions will bubble up errors to the client. Use Zod for validation to catch input errors early.

```typescript
import { z } from 'zod';

const Schema = z.object({ ... });

export const myFn = createServerFn("POST", async (input) => {
  const data = Schema.parse(input);
  // ...
});
```
