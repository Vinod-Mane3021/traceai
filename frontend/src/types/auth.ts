export interface AuthUser {
  username: string;
  avatar_url: string;
  installation_id?: number;
}

export interface AuthCallbackResponse {
  access_token: string;
  user: AuthUser;
}
