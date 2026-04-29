import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/fetch-api";
import { env } from "@/lib/env";
import { mockAuthCallback } from "../lib/mock-auth";
import { useAuthStore } from "../store/auth-store";
import type { AuthCallbackResponse } from "@/types/auth";

interface ExchangeParams {
  code: string;
  redirect_uri: string;
}

async function exchangeCode({ code, redirect_uri }: ExchangeParams): Promise<AuthCallbackResponse> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 600));
    return mockAuthCallback;
  }
  return apiRequest<AuthCallbackResponse>("/v1/auth/github/callback", {
    method: "POST",
    body: JSON.stringify({ code, redirect_uri }),
  });
}

export function useGithubCallback() {
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: (params: ExchangeParams) => exchangeCode(params),
    onSuccess: (data) => setSession(data.access_token, data.user),
  });
}
