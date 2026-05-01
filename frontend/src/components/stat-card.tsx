import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: React.ReactNode;
  value: number | string;
  icon: LucideIcon;
  hint?: React.ReactNode;
  tone?: "default" | "critical" | "success" | "warning";
  index?: number;
}

const tones = {
  default: "text-foreground",
  critical: "text-[color:var(--sev-critical)]",
  success: "text-success",
  warning: "text-warning",
};

export function StatCard({ label, value, icon: Icon, hint, tone = "default", index = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05, ease: "easeOut" }}
      className="rounded-xl border border-border bg-card p-5 hover:border-primary/40 transition-colors"
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {label}
        </span>
        <Icon className={cn("h-4 w-4", tones[tone])} />
      </div>
      <div className={cn("mt-3 text-3xl font-semibold tracking-tight", tones[tone])}>
        {value}
      </div>
      {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </motion.div>
  );
}
