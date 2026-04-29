import type { CustomRule } from "@/types/rule";

export const mockRules: CustomRule[] = [
  {
    id: 1,
    repository_id: 1296269,
    rule_text: "Never use MD5 hashing, enforce SHA-256.",
    is_active: true,
    created_at: "2024-05-20T10:00:00Z",
  },
  {
    id: 2,
    repository_id: 1296269,
    rule_text: "Enforce strict typing in all TypeScript files.",
    is_active: true,
    created_at: "2024-05-20T11:00:00Z",
  },
  {
    id: 3,
    repository_id: 1296270,
    rule_text: "All Stripe webhook handlers must verify signatures.",
    is_active: true,
    created_at: "2024-05-21T09:30:00Z",
  },
  {
    id: 4,
    repository_id: 1296270,
    rule_text: "Reject any usage of eval() or new Function().",
    is_active: false,
    created_at: "2024-05-22T14:10:00Z",
  },
  {
    id: 5,
    repository_id: 1296271,
    rule_text: "JWT secrets must be loaded from env, never hard-coded.",
    is_active: true,
    created_at: "2024-05-23T08:00:00Z",
  },
];

let nextId = 6;
const store: CustomRule[] = [...mockRules];

export const mockRuleStore = {
  list(repoId?: number) {
    return repoId ? store.filter((r) => r.repository_id === repoId) : [...store];
  },
  get(id: number) {
    return store.find((r) => r.id === id);
  },
  create(input: { repository_id: number; rule_text: string; is_active: boolean }) {
    const rule: CustomRule = {
      id: nextId++,
      repository_id: input.repository_id,
      rule_text: input.rule_text,
      is_active: input.is_active,
      created_at: new Date().toISOString(),
    };
    store.unshift(rule);
    return rule;
  },
  update(id: number, patch: { rule_text?: string; is_active?: boolean }) {
    const idx = store.findIndex((r) => r.id === id);
    if (idx === -1) throw new Error("Rule not found");
    store[idx] = { ...store[idx], ...patch };
    return store[idx];
  },
  remove(id: number) {
    const idx = store.findIndex((r) => r.id === id);
    if (idx !== -1) store.splice(idx, 1);
  },
};
