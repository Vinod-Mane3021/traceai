import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockRuleStore } from "../lib/mock-rules";
import type { CreateCustomRuleInput, CustomRule } from "@/types/rule";

async function createRule(input: CreateCustomRuleInput): Promise<CustomRule> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 250));
    return mockRuleStore.create(input);
  }
  return apiRequest<CustomRule>("/v1/rules/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function useCreateRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createRule,
    onSuccess: (rule) => {
      qc.invalidateQueries({ queryKey: ["rules", "by-repository", rule.repository_id] });
    },
  });
}
