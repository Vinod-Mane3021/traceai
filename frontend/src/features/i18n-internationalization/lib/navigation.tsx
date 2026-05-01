import * as React from "react";
import { Link as RouterLink, useNavigate as useRouterNavigate } from "@tanstack/react-router";
import { useTranslation } from "./provider";

export function Link({ to, params, ...props }: any) {
  const { locale } = useTranslation();
  return <RouterLink to={to} params={{ locale, ...params }} {...props} />;
}

export function useNavigate() {
  const navigate = useRouterNavigate();
  const { locale } = useTranslation();

  return (opts: any) =>
    navigate({
      ...opts,
      params: { locale, ...opts.params },
    });
}
