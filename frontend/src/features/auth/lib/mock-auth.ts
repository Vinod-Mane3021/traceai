import type { AuthCallbackResponse } from "@/types/auth";

export const mockAuthCallback: AuthCallbackResponse = {
  access_token: "mock.jwt.token.signature",
  user: {
    username: "octocat",
    avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
  },
};
