export interface ApiInfo {
  name: string;
  description: string;
  version: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}
