export interface RepoOwner {
  login: string;
  id: number;
  avatar_url: string;
}

export interface Repository {
  id: number;
  name: string;
  full_name: string;
  private: boolean;
  owner: RepoOwner;
  html_url: string;
  description: string | null;
}
