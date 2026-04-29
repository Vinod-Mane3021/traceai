import type { Repository } from "@/types/repository";

export const mockRepositories: Repository[] = [
  {
    id: 1296269,
    name: "my-secure-app",
    full_name: "octocat/my-secure-app",
    private: false,
    owner: {
      login: "octocat",
      id: 1,
      avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
    },
    html_url: "https://github.com/octocat/my-secure-app",
    description: "Reference application protected by Trace.ai",
  },
  {
    id: 1296270,
    name: "billing-service",
    full_name: "octocat/billing-service",
    private: true,
    owner: {
      login: "octocat",
      id: 1,
      avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
    },
    html_url: "https://github.com/octocat/billing-service",
    description: "Stripe-powered billing micro-service",
  },
  {
    id: 1296271,
    name: "auth-gateway",
    full_name: "octocat/auth-gateway",
    private: true,
    owner: {
      login: "octocat",
      id: 1,
      avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
    },
    html_url: "https://github.com/octocat/auth-gateway",
    description: "Edge auth + JWT issuance",
  },
  {
    id: 1296272,
    name: "marketing-site",
    full_name: "octocat/marketing-site",
    private: false,
    owner: {
      login: "octocat",
      id: 1,
      avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
    },
    html_url: "https://github.com/octocat/marketing-site",
    description: "Public marketing website",
  },
  {
    id: 1296273,
    name: "media-service",
    full_name: "octocat/media-service",
    private: true,
    owner: {
      login: "octocat",
      id: 1,
      avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
    },
    html_url: "https://github.com/octocat/media-service",
    description: "Image & video pipeline",
  },
  {
    id: 1296274,
    name: "internal-tools",
    full_name: "octocat/internal-tools",
    private: true,
    owner: {
      login: "octocat",
      id: 1,
      avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
    },
    html_url: "https://github.com/octocat/internal-tools",
    description: "Admin & ops dashboard",
  },
];
