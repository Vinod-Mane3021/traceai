import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockRepositories } from "../lib/mock-repositories";
import { useAuthStore } from "@/features/auth/store/auth-store";
import type { Repository } from "@/types/repository";

async function fetchRepositories(installationId: string): Promise<Repository[]> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 400));
    return mockRepositories;
  }
  
  if (!installationId || installationId === "demo") {
    return [];
  }

  return apiRequest<Repository[]>(
    `/v1/github/repositories?installation_id=${encodeURIComponent(installationId)}`,
  );
}

export function useRepositories(installationId?: string) {
  const user = useAuthStore((s) => s.user);
  
  // Use passed ID, or the one from the user session, or default to "demo"
  const activeId = installationId ?? user?.installation_id?.toString() ?? "demo";

  return useQuery({
    queryKey: ["github", "repositories", activeId],
    queryFn: () => fetchRepositories(activeId),
  });
}
