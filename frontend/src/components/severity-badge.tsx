import type { Severity, VulnStatus } from "@/types/analytics";
import { cn } from "@/lib/utils";

const sevStyles: Record<Severity, string> = {
  CRITICAL: "bg-[color:var(--sev-critical)]/15 text-[color:var(--sev-critical)] border-[color:var(--sev-critical)]/30",
  HIGH: "bg-[color:var(--sev-high)]/15 text-[color:var(--sev-high)] border-[color:var(--sev-high)]/30",
  MEDIUM: "bg-[color:var(--sev-medium)]/15 text-[color:var(--sev-medium)] border-[color:var(--sev-medium)]/30",
  LOW: "bg-[color:var(--sev-low)]/15 text-[color:var(--sev-low)] border-[color:var(--sev-low)]/30",
  INFO: "bg-[color:var(--sev-info)]/15 text-[color:var(--sev-info)] border-[color:var(--sev-info)]/30",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide",
        sevStyles[severity],
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {severity}
    </span>
  );
}

const statusStyles: Record<VulnStatus, string> = {
  OPEN: "bg-destructive/10 text-destructive border-destructive/30",
  IN_PROGRESS: "bg-warning/10 text-warning border-warning/30",
  FIXED: "bg-success/10 text-success border-success/30",
  IGNORED: "bg-muted text-muted-foreground border-border",
};

export function StatusBadge({ status }: { status: VulnStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium",
        statusStyles[status],
      )}
    >
      {status.replace("_", " ")}
    </span>
  );
}
