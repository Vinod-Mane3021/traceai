import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockRuleStore } from "../lib/mock-rules";
import type { CustomRule } from "@/types/rule";

async function fetchRulesByRepository(repositoryId: number): Promise<CustomRule[]> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 300));
    return mockRuleStore.list(repositoryId);
  }
  return apiRequest<CustomRule[]>(`/v1/rules/repository/${repositoryId}`);
}

export function useRulesByRepository(repositoryId: number | null) {
  return useQuery({
    queryKey: ["rules", "by-repository", repositoryId],
    queryFn: () => fetchRulesByRepository(repositoryId as number),
    enabled: repositoryId != null,
  });
}
