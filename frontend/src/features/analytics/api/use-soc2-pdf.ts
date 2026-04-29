import { useMutation } from "@tanstack/react-query";
import { apiBlob } from "@/lib/fetch-api";
import { env } from "@/lib/env";

async function downloadSoc2Pdf(repositoryId: number): Promise<Blob> {
  if (env.mockApi) {
    await new Promise((r) => setTimeout(r, 600));
    const text = `Trace.ai SOC2 Report\nRepository ID: ${repositoryId}\nGenerated: ${new Date().toISOString()}\n\n(Mock PDF placeholder)`;
    return new Blob([text], { type: "application/pdf" });
  }
  return apiBlob(`/v1/analytics/report/soc2/pdf?repository_id=${repositoryId}`);
}

export function useSoc2PdfReport() {
  return useMutation({
    mutationFn: (repositoryId: number) => downloadSoc2Pdf(repositoryId),
    onSuccess: (blob, repositoryId) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `soc2-report-repo-${repositoryId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    },
  });
}
