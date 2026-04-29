import { useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockRuleStore } from "../lib/mock-rules";
import { getAuthToken } from "@/features/auth/store/auth-store";

interface DeleteArgs {
  ruleId: number;
  repositoryId: number;
}

async function deleteRule({ ruleId }: DeleteArgs): Promise<void> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 200));
    mockRuleStore.remove(ruleId);
    return;
  }
  const token = getAuthToken();
  const headers = new Headers();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetchApi(`${env.apiBaseUrl}/v1/rules/${ruleId}`, {
    method: "DELETE",
    headers,
  });
  if (!res.ok && res.status !== 204) {
    throw new Error(`Failed to delete rule (${res.status})`);
  }
}

export function useDeleteRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteRule,
    onSuccess: (_void, vars) => {
      qc.invalidateQueries({ queryKey: ["rules", "by-repository", vars.repositoryId] });
    },
  });
}
