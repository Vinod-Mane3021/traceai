---
description: End-to-end feature implementation following Trace.ai patterns across API, Service, and UI layers.
---

# Feature Builder

You are an expert at implementing complete features in Trace.ai following established patterns across all layers.

You MUST use the specialized skills for each phase while building the feature.

- Logic & Services: `service-builder`
- Forms: `forms-builder`

## Implementation Phases

### Phase 1: Types & Schemas

Define the data structures and validation schemas in the appropriate directories.

1. Create types in `src/types/[feature].ts`.
2. Create Zod schemas in `src/features/[feature]/lib/[feature].schema.ts`.

```typescript
// src/types/project.ts
export interface Project {
  id: string;
  name: string;
  status: 'active' | 'archived';
}

// src/features/projects/lib/project.schema.ts
import { z } from 'zod';
export const CreateProjectSchema = z.object({
  name: z.string().min(1, 'Name is required'),
});
```

### Phase 2: Service Layer

Use `service-builder` skill.

**Rule: Services are decoupled from interfaces.** The service contains the core logic or API interaction wrappers. It should be testable in isolation.

Create in `src/features/[feature]/lib/[feature].service.ts`.

### Phase 3: API Hooks (TanStack Query)

Implement data fetching and mutations.

1. Create hooks in `src/features/[feature]/api/use-[feature].ts`.
2. Use `apiRequest` from `@/lib/fetch-api.ts`.
3. Implement mock support using `env.mockApi`.

```typescript
// src/features/projects/api/use-projects.ts
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockProjects } from "../lib/mock-projects";

async function fetchProjects() {
  if (env.mockApi) {
    return mockProjects;
  }
  return apiRequest<Project[]>("/v1/projects");
}

export function useProjects() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });
}
```

### Phase 4: UI Components

Use `form-builder` skill for form patterns.

Create in `src/features/[feature]/components/` directory:

1. **List component** - Display items with loading states (Skeletons).
2. **Form component** - Create/edit with validation.
3. **Detail component** - Single item view.

### Phase 5: Route Integration (TanStack Router)

Create page in `src/routes/`.

```typescript
// src/routes/_app.projects.tsx
import { createFileRoute } from "@tanstack/react-router";
import { ProjectList } from "@/features/projects/components/project-list";

export const Route = createFileRoute("/_app/projects")({
  component: ProjectsPage,
});

function ProjectsPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Projects</h1>
      <ProjectList />
    </div>
  );
}
```

## File Structure

```
src/
├── types/
│   └── feature.ts
├── features/
│   └── feature/
│       ├── api/
│       │   ├── use-feature.ts
│       │   └── use-create-feature.ts
│       ├── components/
│       │   ├── feature-list.tsx
│       │   └── feature-form.tsx
│       └── lib/
│           ├── feature.service.ts
│           ├── feature.schema.ts
│           └── mock-feature.ts
└── routes/
    └── _app.feature.tsx
```

## Verification Checklist

### API & Logic Layer

- [ ] Types defined in `src/types/`
- [ ] Zod schema in `src/features/[feature]/lib/`
- [ ] Service class or functions in `src/features/[feature]/lib/`
- [ ] API hooks use TanStack Query (`useQuery`, `useMutation`)
- [ ] Hooks use `apiRequest` utility
- [ ] Mock data implemented and toggled via `env.mockApi`
- [ ] Query invalidation handled in `onSuccess` for mutations

### UI Layer

- [ ] Components in `src/features/[feature]/components/` directory
- [ ] Forms use `react-hook-form` with `zodResolver`
- [ ] Loading states handled with Skeletons or `Loader2`
- [ ] Error display for failed requests
- [ ] `data-test` attributes for E2E testing
- [ ] Styling uses Tailwind 4 utilities and project-specific classes (`.glass`, etc.)
- [ ] Lucide icons used consistently

### Page & Routing

- [ ] Route added in `src/routes/`
- [ ] `createFileRoute` used with correct path
- [ ] Meta tags/Head configured if needed
- [ ] `Topbar` or other layout components integrated

### Final Verification

```bash
# Type check
npm run tsc -- --noEmit

# Lint
npm run lint

# Format
npm run format
```

When you are done, run the code quality reviewer agent to verify the code quality.
