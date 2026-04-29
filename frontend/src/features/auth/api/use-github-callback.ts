import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockAuthCallback } from "../lib/mock-auth";
import { useAuthStore } from "../store/auth-store";
import type { AuthCallbackResponse } from "@/types/auth";

async function exchangeCode(code: string): Promise<AuthCallbackResponse> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 600));
    return mockAuthCallback;
  }
  return apiRequest<AuthCallbackResponse>("/v1/auth/github/callback", {
    method: "GET",
    body: JSON.stringify({ code }),
  });
}

export function useGithubCallback() {
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: (code: string) => exchangeCode(code),
    onSuccess: (data) => setSession(data.access_token, data.user),
  });
}
