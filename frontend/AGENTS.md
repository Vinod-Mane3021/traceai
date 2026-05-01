# Trace.ai Frontend Rules (Master AI Index)

This is the primary entry point for Gemini CLI and other AI agents. 
AI: ALWAYS read the relevant skill files in `.claude/` before starting any major task.

## 🚀 Specialized Technical Skills (The Manuals)
When performing these tasks, follow the step-by-step guides in the `.claude/` folder:

- **End-to-End Features**: Use `.claude/commands/feature-builder.md` (TanStack patterns)
- **Quality Review**: Use `.claude/agents/code-quality-reviewer.md` (Mandatory after every task)
- **Database/Postgres**: `.claude/skills/postgres-expert/SKILL.md`
- **Logic & Services**: `.claude/skills/service-builder/SKILL.md` (Injected dependencies pattern)
- **Forms**: `.claude/skills/react-form-builder/SKILL.md` (React Hook Form + Zod patterns)

---

## 💻 Tech Stack
- **Framework**: TanStack Start (React 19 + TanStack Router)
- **State Management**: TanStack Query (Server State), Zustand (Client State)
- **Styling**: Tailwind CSS 4 (using @tailwindcss/vite)
- **UI Components**: Radix UI primitives via Shadcn/UI (in `src/components/ui`)
- **Forms**: React Hook Form + Zod

## 📂 Project Structure
- `src/features/`: Feature-based logic, components, and API hooks.
- `src/routes/`: File-based routing (TanStack Router).
- `src/components/ui/`: Reusable base UI components.
- `src/lib/`: Shared utility functions and clients (QueryClient, API fetcher, etc.).

## 🛠️ Development Workflow
1. **Feature First**: Place logic, components, and API hooks inside the relevant feature folder in `src/features/`.
2. **Logic Separation**: Use the **Service Pattern** from `.claude/skills/service-builder/SKILL.md`. Keep business logic in `*.service.ts` files, decoupled from the UI.
3. **Routing**: Add new routes in `src/routes/`. TanStack Router generates types automatically.
4. **API Hooks**: Use TanStack Query. Standardize on `use-[feature-name].ts` naming convention.
5. **Styling**: Use Tailwind 4. Utilize utilities like `.glass`, `.grid-bg`, and `.ring-soft` for consistent effects.
   - **Severity Colors**: `sev-critical`, `sev-high`, `sev-medium`, `sev-low`, `sev-info`.

## 🔒 Security & Data Fetching
- **API Calls**: Use the `apiRequest` utility from `@/lib/fetch-api.ts`.
- **Mocking**: Support for local development via `env.mockApi` (toggled by `VITE_MOCK_API_CALLS`).
- **Authorization**: Token-based auth managed via `useAuthStore` in `src/features/auth/store/auth-store.ts`.

## 📜 Coding Standards (Non-Negotiables)
- **TypeScript**: Strict typing mandatory. Absolutely no `any`.
- **Patterns**: Follow the **"Trace.ai Non-negotiables"** found in the `.claude/` skill files.
- **Components**: Functional components with arrow functions. Use `cn` for class merging.
- **Validation**: Use Zod for all forms and API response schemas.

## ✅ Verification & Review
1. **Self-Review**: Read `.claude/agents/code-quality-reviewer.md` and check your work against it.
2. **Lint & Typecheck**: Run `npm run lint` and `tsc --noEmit`.
3. **Accessibility**: Ensure all new components are responsive and accessible.
