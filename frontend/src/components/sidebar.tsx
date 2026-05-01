import * as React from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, GitBranch, ShieldAlert, ScrollText, Settings } from "lucide-react";
import { env } from "@/lib/env";
import { cn } from "@/lib/utils";

const items = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/repositories", label: "Repositories", icon: GitBranch },
  { to: "/vulnerabilities", label: "Vulnerabilities", icon: ShieldAlert },
  { to: "/rules", label: "Rules", icon: ScrollText },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function Sidebar() {
  const path = useRouterState({ select: (s) => s.location.pathname });

  return (
    <aside className="hidden md:flex md:w-60 lg:w-64 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="px-5 py-5 flex items-center gap-2">
        <div className="grid h-8 w-8 place-items-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
          <span className="font-mono text-sm font-bold">T</span>
        </div>
        <div className="leading-tight">
          <div className="text-sm font-semibold">{env.appName}</div>
          <div className="text-[11px] text-muted-foreground">
            security console
          </div>
        </div>
      </div>
      <nav className="px-3 py-2 space-y-0.5">
        {items.map((item) => {
          const active = path === item.to || (item.to !== "/" && path.startsWith(item.to));
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
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto p-4 text-[11px] text-muted-foreground">
        Version ·{" "}
        {env.mockApi ? "Mock Data" : "Live"}
      </div>
    </aside>
  );
}

