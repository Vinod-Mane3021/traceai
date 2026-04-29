import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import type { ApiInfo } from "@/types/common";

async function fetchApiInfo(): Promise<ApiInfo> {
  if (env.mockApi) {
    return {
      name: "trace-ai-backend",
      description: "AI-powered security scanning for GitHub PRs",
      version: "1.0.0",
    };
  }
  return apiRequest<ApiInfo>("/");
}

export function useApiInfo() {
  return useQuery({ queryKey: ["api", "info"], queryFn: fetchApiInfo });
}
