import { User } from '../user/user';

export class Repository {
  id: number;
  name: string;
  full_name: string;
  language: string;
  updated_at: string;
  created_at: string;
  html_url: string;
  description: string;
  owner: User;
  url: string;
  contents_url: string;
  auto_init: boolean;
}