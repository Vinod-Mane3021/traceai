import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockRuleStore } from "../lib/mock-rules";
import type { CustomRule, UpdateCustomRuleInput } from "@/types/rule";

interface UpdateArgs {
  ruleId: number;
  patch: UpdateCustomRuleInput;
}

async function updateRule({ ruleId, patch }: UpdateArgs): Promise<CustomRule> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 200));
    return mockRuleStore.update(ruleId, patch);
  }
  return apiRequest<CustomRule>(`/v1/rules/${ruleId}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function useUpdateRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: updateRule,
    onSuccess: (rule) => {
      qc.invalidateQueries({ queryKey: ["rules", "by-repository", rule.repository_id] });
      qc.invalidateQueries({ queryKey: ["rules", "detail", rule.id] });
    },
  });
}
