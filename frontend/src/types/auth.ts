export interface AuthUser {
  username: string;
  avatar_url: string;
}

export interface AuthCallbackResponse {
  access_token: string;
  user: AuthUser;
}
