import { useMutation } from "@tanstack/react-query";
import { apiBlob } from "@/lib/fetch-api";
import { env } from "@/lib/env";

async function downloadSoc2Pdf(githubId: number): Promise<Blob> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 600));
    const text = `Trace.ai SOC2 Report\nRepository ID: ${githubId}\nGenerated: ${new Date().toISOString()}\n\n(Mock PDF placeholder)`;
    return new Blob([text], { type: "application/pdf" });
  }
  return apiBlob(`/v1/analytics/report/soc2/pdf?github_id=${githubId}`);
}

export function useSoc2PdfReport() {
  return useMutation({
    mutationFn: (githubId: number) => downloadSoc2Pdf(githubId),
    onSuccess: (blob, githubId) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `soc2-report-repo-${githubId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    },
  });
}
