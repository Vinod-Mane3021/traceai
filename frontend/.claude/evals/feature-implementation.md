# Agent Evaluation: Full Feature Implementation (Trace.ai)

This eval tests whether the agent correctly follows Trace.ai patterns when implementing a complete feature spanning API hooks, services, and UI layers.

## Task: Implement "Custom Rules" Feature

### Prompt

```
Implement a "Custom Rules" feature for repositories with the following requirements:

1. API Hook: useRules hook to fetch rules for a repository, and useCreateRule hook for adding new rules.
2. Service: RuleService to handle rule validation and API requests.
3. UI: Rules list component and a creation form.
4. Route: Feature should be accessible at /rules.

Use the available skills for guidance.
```

---

## Success Criteria (Grading Rubric)

### 1. Logic & Service Layer (25 points)

| Criterion | Points | Pass Condition |
|-----------|--------|----------------|
| Types defined in `src/types/rule.ts` | 5 | File exists with proper interfaces |
| RuleService created in `src/features/rules/lib/` | 5 | File exists, uses class or factory function |
| Service decouples API requests | 5 | `apiRequest` is injected or passed as param |
| Service contains business logic | 5 | Validation or transformation logic present |
| Mock data provided in `mock-rules.ts` | 5 | Used when `env.mockApi` is true |

### 2. API & Hook Layer (25 points)

| Criterion | Points | Pass Condition |
|-----------|--------|----------------|
| Hooks in `src/features/rules/api/` | 5 | `use-rules.ts` and `use-create-rule.ts` exist |
| Uses TanStack Query (`useQuery`, `useMutation`) | 10 | Correct usage of query keys and mutation functions |
| Invalidates queries on success | 5 | `onSuccess` calls `qc.invalidateQueries` |
| Uses `apiRequest` from `@/lib/fetch-api.ts` | 5 | Standard API utility used |

### 3. UI Layer (25 points)

| Criterion | Points | Pass Condition |
|-----------|--------|----------------|
| Components in `src/features/rules/components/` | 5 | Correct directory structure |
| Form uses `react-hook-form` + `zodResolver` | 5 | Type-safe form validation |
| Uses `@/components/ui/form` components | 5 | Standard UI components used |
| Loading states implemented | 5 | Skeletons or `Loader2` used |
| `data-test` attributes added | 5 | Present for E2E testing |

### 4. Integration & Routing (15 points)

| Criterion | Points | Pass Condition |
|-----------|--------|----------------|
| Route in `src/routes/_app.rules.tsx` | 5 | Correct path and TanStack Router usage |
| Tailwind 4 styling applied | 5 | Uses project utilities (`.glass`, etc.) |
| Lucide icons used | 5 | Consistent icon usage |

### 5. Code Quality (10 points)

| Criterion | Points | Pass Condition |
|-----------|--------|----------------|
| No `any` types | 5 | Strict TypeScript |
| Feature-first organization | 5 | Logic kept within the feature folder |

---

## Verification & Review

The agent should run the `code-quality-reviewer` after implementation to self-correct.
