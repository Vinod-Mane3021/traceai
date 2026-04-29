import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockRuleStore } from "../lib/mock-rules";
import type { CustomRule } from "@/types/rule";

async function fetchRule(ruleId: number): Promise<CustomRule> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 200));
    const rule = mockRuleStore.get(ruleId);
    if (!rule) throw new Error("Rule not found");
    return rule;
  }
  return apiRequest<CustomRule>(`/v1/rules/${ruleId}`);
}

export function useRule(ruleId: number | null) {
  return useQuery({
    queryKey: ["rules", "detail", ruleId],
    queryFn: () => fetchRule(ruleId as number),
    enabled: ruleId != null,
  });
}
