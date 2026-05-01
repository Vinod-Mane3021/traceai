const messageFiles = import.meta.glob("../messages/**/*.json");

export async function loadMessages(locale: string) {
  const messages: Record<string, any> = {};

  // Find all files for this locale (e.g. ../messages/en/common.json)
  const localeFiles = Object.keys(messageFiles).filter((path) =>
    path.includes(`/messages/${locale}/`)
  );

  for (const path of localeFiles) {
    const module: any = await messageFiles[path]();
    // Extract filename as namespace (e.g. "common" from "common.json")
    const filename = path.split("/").pop()?.replace(".json", "") || "";
    messages[filename] = module.default || module;
  }

  // Ensure common always exists as a fallback
  if (!messages.common) {
    messages.common = {};
  }

  return messages;
}
