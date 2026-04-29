export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
export type VulnStatus = "OPEN" | "FIXED" | "IGNORED" | "IN_PROGRESS";

export interface Vulnerability {
  id: number;
  title: string;
  severity: Severity;
  status: VulnStatus;
  repository: string;
  created_at: string;
}

export interface AnalyticsOverview {
  total_repositories: number;
  total_vulnerabilities: number;
  open_vulnerabilities: number;
  scanned_prs: number;
  critical_vulnerabilities: number;
}
