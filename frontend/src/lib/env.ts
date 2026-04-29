export const env = {
  appName: import.meta.env.VITE_APP_NAME ?? "App",
  appDescription: import.meta.env.VITE_APP_DESCRIPTION ?? "",
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  mockApi: String(import.meta.env.VITE_MOCK_API_CALLS).toLowerCase() === "true",
};
