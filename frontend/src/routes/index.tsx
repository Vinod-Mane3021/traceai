import * as React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { defaultLocale } from "../features/i18n-internationalization/lib/locales";

export const Route = createFileRoute("/")({
  beforeLoad: () => {
    throw redirect({
      to: "/$locale",
      params: { locale: defaultLocale },
    });
  },
});
