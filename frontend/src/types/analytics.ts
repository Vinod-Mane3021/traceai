export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO" | "critical" | "high" | "medium" | "low" | "info";
export type VulnStatus = "OPEN" | "FIXED" | "IGNORED" | "IN_PROGRESS" | "open" | "fixed" | "ignored" | "in_progress";

export interface Vulnerability {
  id: number;
  file_path: string;
  line_number?: number;
  pull_request_id?: number;
  description: string;
  severity: Severity;
  status: VulnStatus;
  created_at: string;
  updated_at?: string | null;
}

export interface VulnerabilityFeedResponse {
  recent_vulnerabilities: Vulnerability[];
}

export interface AnalyticsOverview {
  summary: {
    total_vulnerabilities: number;
    total_prs_scanned: number;
    total_repos_monitored: number;
    open_vulnerabilities: number;
  };
  severity_distribution: Array<{
    severity: Severity;
    count: number;
  }>;
  status_distribution: Array<{
    status: VulnStatus;
    count: number;
  }>;
  top_vulnerable_files: Array<{
    file_path: string;
    issue_count: number;
  }>;
  vulnerabilities_by_repo: Array<{
    repo_name: string;
    count: number;
  }>;
}
