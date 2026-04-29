import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockOverview } from "../lib/mock-analytics";
import type { AnalyticsOverview } from "@/types/analytics";

async function fetchOverview(): Promise<AnalyticsOverview> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 350));
    return mockOverview;
  }
  return apiRequest<AnalyticsOverview>("/v1/analytics/overview");
}

export function useAnalyticsOverview() {
  return useQuery({
    queryKey: ["analytics", "overview"],
    queryFn: fetchOverview,
  });
}
