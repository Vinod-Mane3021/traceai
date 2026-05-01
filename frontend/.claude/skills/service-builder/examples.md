# Service Builder Examples (Trace.ai)

## Service with API Injected

```typescript
// src/features/repositories/lib/repository.service.ts
import { Repository } from "@/types/repository";
import { ApiRequester } from "./rule.service";

export function createRepositoryService(apiRequest: ApiRequester) {
  return new RepositoryService(apiRequest);
}

class RepositoryService {
  constructor(private readonly apiRequest: ApiRequester) {}

  async getRepository(id: string): Promise<Repository> {
    return this.apiRequest<Repository>(`/v1/github/repositories/${id}`);
  }

  async syncRepository(id: string): Promise<void> {
    await this.apiRequest(`/v1/github/repositories/${id}/sync`, {
      method: 'POST'
    });
  }
}
```

## Integration with TanStack Query Hook

```typescript
// src/features/repositories/api/use-repository.ts
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { createRepositoryService } from "../lib/repository.service";

export function useRepository(id: string) {
  const service = createRepositoryService(apiRequest);
  
  return useQuery({
    queryKey: ["repositories", id],
    queryFn: () => service.getRepository(id),
    enabled: !!id,
  });
}
```

## Testing with Vitest

```typescript
// src/features/repositories/lib/__tests__/repository.service.test.ts
import { describe, it, expect, vi } from 'vitest';
import { createRepositoryService } from '../repository.service';

describe('RepositoryService', () => {
  it('fetches repository by id', async () => {
    const mockRepo = { id: '123', name: 'trace-ai' };
    const mockApi = vi.fn().mockResolvedValue(mockRepo);
    const service = createRepositoryService(mockApi);

    const result = await service.getRepository('123');

    expect(result).toEqual(mockRepo);
    expect(mockApi).toHaveBeenCalledWith('/v1/github/repositories/123');
  });
});
```

## Pure Logic Service (No I/O)

```typescript
// src/features/analytics/lib/vulnerability-processor.service.ts
import { Vulnerability } from "@/types/analytics";

export function processVulnerabilities(vulns: Vulnerability[]) {
  return vulns.sort((a, b) => b.severity_score - a.severity_score);
}
```

Usage in a component or hook:
```typescript
const sortedVulns = processVulnerabilities(data ?? []);
```
