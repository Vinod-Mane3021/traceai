import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Plus, Trash2, Check, X, Pencil } from "lucide-react";
import { useRulesByRepository } from "../api/use-rules-by-repository";
import { useCreateRule } from "../api/use-create-rule";
import { useUpdateRule } from "../api/use-update-rule";
import { useDeleteRule } from "../api/use-delete-rule";
import { Skeleton } from "@/components/skeleton-block";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import type { CustomRule } from "@/types/rule";
import { Trans } from "@/features/i18n-internationalization/components/trans";
import { useTranslation } from "@/features/i18n-internationalization/lib/provider";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function RuleList({ repositoryId }: { repositoryId: number }) {
  const { data, isLoading, isError } = useRulesByRepository(repositoryId);
  const createRule = useCreateRule();
  const [draft, setDraft] = useState("");
  const [active, setActive] = useState(true);
  const { t } = useTranslation();

  const onCreate = () => {
    const text = draft.trim();
    if (!text) return;
    createRule.mutate(
      { repository_id: repositoryId, rule_text: text, is_active: active },
      {
        onSuccess: () => {
          setDraft("");
          setActive(true);
        },
      },
    );
  };

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-border bg-card p-4 sm:p-5">
        <h3 className="text-sm font-semibold tracking-tight">
          <Trans i18nKey="rules:list.add_title" />
        </h3>
        <p className="mt-1 text-xs text-muted-foreground">
          <Trans i18nKey="rules:list.add_description" />
        </p>
        <div className="mt-3 grid gap-3">
          <Textarea
            placeholder={t("rules:list.placeholder")}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={3}
            className="resize-none"
          />
          <div className="flex items-center justify-between gap-3">
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              <Switch checked={active} onCheckedChange={setActive} />
              <span>
                {active ? (
                  <Trans i18nKey="rules:list.active" />
                ) : (
                  <Trans i18nKey="rules:list.inactive" />
                )}
              </span>
            </label>
            <Button size="sm" onClick={onCreate} disabled={!draft.trim() || createRule.isPending}>
              {createRule.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              <span className="ml-1.5">
                <Trans i18nKey="rules:list.add_button" />
              </span>
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold tracking-tight">
            <Trans i18nKey="rules:list.rules_title" />
          </h3>
          <span className="text-xs text-muted-foreground">
            <Trans i18nKey="rules:list.total" values={{ count: data?.length ?? 0 }} />
          </span>
        </div>

        {isLoading ? (
          <div className="grid gap-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        ) : isError ? (
          <p className="text-sm text-destructive">
            <Trans i18nKey="common:errors.failed_load_rules" />
          </p>
        ) : !data || data.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border bg-card/40 p-8 text-center">
            <p className="text-sm text-muted-foreground">
              <Trans i18nKey="rules:list.no_rules" />
            </p>
          </div>
        ) : (
          <div className="grid gap-2">
            <AnimatePresence initial={false}>
              {data.map((rule, i) => (
                <motion.div
                  key={rule.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ delay: i * 0.02 }}
                >
                  <RuleRow rule={rule} />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}

function RuleRow({ rule }: { rule: CustomRule }) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(rule.rule_text);
  const updateRule = useUpdateRule();
  const deleteRule = useDeleteRule();
  const { t } = useTranslation();

  const onSave = () => {
    const tVal = text.trim();
    if (!tVal || tVal === rule.rule_text) {
      setEditing(false);
      return;
    }
    updateRule.mutate(
      { ruleId: rule.id, patch: { rule_text: tVal } },
      { onSuccess: () => setEditing(false) },
    );
  };

  const onToggle = (checked: boolean) => {
    updateRule.mutate({ ruleId: rule.id, patch: { is_active: checked } });
  };

  const onDelete = () => {
    if (!confirm(t("rules:list.delete_confirm"))) return;
    deleteRule.mutate({ ruleId: rule.id, repositoryId: rule.repository_id });
  };

  return (
    <div className="rounded-xl border border-border bg-card p-4 hover:border-primary/40 transition-colors">
      <div className="flex items-start gap-3">
        <div className="min-w-0 flex-1">
          {editing ? (
            <Input
              autoFocus
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") onSave();
                if (e.key === "Escape") {
                  setText(rule.rule_text);
                  setEditing(false);
                }
              }}
            />
          ) : (
            <p className="text-sm leading-relaxed text-foreground">{rule.rule_text}</p>
          )}
          <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-muted-foreground">
            <span>
              <Trans i18nKey="rules:list.added_at" values={{ date: formatDate(rule.created_at) }} />
            </span>
            <span className="font-mono">#{rule.id}</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <Switch checked={rule.is_active} onCheckedChange={onToggle} disabled={updateRule.isPending} />
          {editing ? (
            <>
              <Button size="sm" variant="ghost" onClick={onSave} disabled={updateRule.isPending}>
                {updateRule.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Check className="h-4 w-4" />
                )}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setText(rule.rule_text);
                  setEditing(false);
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <>
              <Button size="sm" variant="ghost" onClick={() => setEditing(true)}>
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={onDelete}
                disabled={deleteRule.isPending}
                className="text-destructive hover:text-destructive"
              >
                {deleteRule.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

