import { createServerFn } from "@tanstack/react-start";
import { getCookie, setCookie } from "@tanstack/react-start/server";
import * as z from "zod";

const themeSchema = z.union([z.literal("light"), z.literal("dark")]);
export type Theme = z.infer<typeof themeSchema>;

const storageKey = "_preferred-theme";

export const getThemeServerFn = createServerFn({
  method: "GET",
}).handler(async () => {
  return (getCookie(storageKey) || "dark") as Theme;
});

export const setThemeServerFn = createServerFn({
  method: "POST",
})
  .inputValidator(themeSchema)
  .handler(async ({ data }) => {
    setCookie(storageKey, data);
  });
