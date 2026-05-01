import * as React from "react";
import { Link } from "@/features/i18n-internationalization/lib/navigation";
import { useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, GitBranch, ShieldAlert, ScrollText, Settings } from "lucide-react";
import { env } from "@/lib/env";
import { cn } from "@/lib/utils";
import { useTranslation } from "@/features/i18n-internationalization/lib/provider";
import { Trans } from "@/features/i18n-internationalization/components/trans";

const items = [
  { to: "/$locale/", labelKey: "common:nav.dashboard", icon: LayoutDashboard },
  { to: "/$locale/repositories", labelKey: "common:nav.repositories", icon: GitBranch },
  { to: "/$locale/vulnerabilities", labelKey: "common:nav.vulnerabilities", icon: ShieldAlert },
  { to: "/$locale/rules", labelKey: "common:nav.rules", icon: ScrollText },
  { to: "/$locale/settings", labelKey: "common:nav.settings", icon: Settings },
] as const;

export function Sidebar() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const { locale } = useTranslation();

  return (
    <aside className="hidden md:flex md:w-60 lg:w-64 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="px-5 py-5 flex items-center gap-2">
        <div className="grid h-8 w-8 place-items-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
          <span className="font-mono text-sm font-bold">T</span>
        </div>
        <div className="leading-tight">
          <div className="text-sm font-semibold">{env.appName}</div>
          <div className="text-[11px] text-muted-foreground">
            <Trans i18nKey="common:nav.security_console" />
          </div>
        </div>
      </div>
      <nav className="px-3 py-2 space-y-0.5">
        {items.map((item) => {
          // Simplistic active check, could be improved
          const active = path.includes(item.to.replace("/$locale", `/${locale}`));
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                "group flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm transition-colors",
                active
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              <span>
                <Trans i18nKey={item.labelKey} />
              </span>
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto p-4 text-[11px] text-muted-foreground">
        <Trans i18nKey="common:footer.version" /> ·{" "}
        {env.mockApi ? (
          <Trans i18nKey="common:footer.mock_data" />
        ) : (
          <Trans i18nKey="common:footer.live" />
        )}
      </div>
    </aside>
  );
}

