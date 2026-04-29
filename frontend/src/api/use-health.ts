import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import type { HealthResponse } from "@/types/common";

async function fetchHealth(): Promise<HealthResponse> {
  if (env.mockApi) {
    return { status: "Healthy", service: "trace-ai-backend", version: "1.0.0" };
  }
  return apiRequest<HealthResponse>("/health");
}

export function useHealth() {
  return useQuery({
    queryKey: ["api", "health"],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
  });
}
