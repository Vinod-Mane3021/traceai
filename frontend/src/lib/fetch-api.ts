import { env } from "./env";
import { getAuthToken } from "@/features/auth/store/auth-store";

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
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(text || `Request failed with ${res.status}`);
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
