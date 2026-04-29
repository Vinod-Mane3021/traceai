export interface CustomRule {
  id: number;
  repository_id: number;
  rule_text: string;
  is_active: boolean;
  created_at: string;
}

export interface CreateCustomRuleInput {
  repository_id: number;
  rule_text: string;
  is_active: boolean;
}

export interface UpdateCustomRuleInput {
  rule_text?: string;
  is_active?: boolean;
}
