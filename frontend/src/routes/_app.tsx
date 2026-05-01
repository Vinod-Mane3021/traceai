import * as React from "react";
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { Sidebar } from "@/components/sidebar";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const Route = createFileRoute("/_app")({
  beforeLoad: () => {
    if (typeof window === "undefined") return;
    const token = useAuthStore.getState().token;
    if (!token) {
      throw redirect({
        to: "/login",
      });
    }
  },
  component: AppShell,
});

function AppShell() {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Outlet />
      </div>
    </div>
  );
}
