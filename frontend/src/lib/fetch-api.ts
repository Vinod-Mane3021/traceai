import { env } from "./env";
import { getAuthToken, useAuthStore } from "@/features/auth/store/auth-store";

export const fetchApi = async (
  input: string | URL | Request,
  init?: RequestInit,
): Promise<Response> => {
  const response = await fetch(input, init);
  return response;
};

/**
 * Convenience wrapper that:
 * - prepends VITE_API_BASE_URL when input is a relative path
 * - injects the bearer token from the auth store when present
 * - parses JSON or throws an Error with the response text on non-2xx
 * - handles 401 Unauthorized by clearing the session
 */
export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = path.startsWith("http") ? path : `${env.apiBaseUrl}${path}`;
  const token = getAuthToken();

  const headers = new Headers(init.headers ?? {});
  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetchApi(url, { ...init, headers });

  if (res.status === 401) {
    useAuthStore.getState().clearSession();
    // Optional: could force a reload or redirect here if needed
    // window.location.href = '/login';
  }

  if (!res.ok) {
    let errorMessage = `Request failed with ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData && typeof errorData.detail === "string") {
        errorMessage = errorData.detail;
      } else if (errorData && typeof errorData.detail === "object") {
        errorMessage = JSON.stringify(errorData.detail);
      }
    } catch {
      errorMessage = (await res.text().catch(() => "")) || errorMessage;
    }
    throw new Error(errorMessage);
  }
  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) return (await res.json()) as T;
  return (await res.text()) as unknown as T;
}

export async function apiBlob(path: string, init: RequestInit = {}): Promise<Blob> {
  const url = path.startsWith("http") ? path : `${env.apiBaseUrl}${path}`;
  const token = getAuthToken();
  const headers = new Headers(init.headers ?? {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetchApi(url, { ...init, headers });
  if (!res.ok) throw new Error(`Request failed with ${res.status}`);
  return res.blob();
}
