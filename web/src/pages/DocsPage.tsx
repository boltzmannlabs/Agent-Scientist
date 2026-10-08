import { useLayoutEffect } from "react";
import { useI18n } from "@/i18n";
import { usePageHeader } from "@/contexts/usePageHeader";
import { Markdown } from "@/components/Markdown";
import { PluginSlot } from "@/plugins";
import manual from "../../../README.md?raw";

export default function DocsPage() {
  const { t } = useI18n();
  const { setEnd } = usePageHeader();

  useLayoutEffect(() => {
    setEnd(null);
    return () => setEnd(null);
  }, [setEnd]);

  return (
    <div className="min-h-0 flex-1 overflow-auto p-4 sm:p-6">
      <PluginSlot name="docs:top" />
      <article aria-label={t.app.nav.documentation} className="mx-auto max-w-4xl">
        <Markdown content={manual} />
      </article>
      <PluginSlot name="docs:bottom" />
    </div>
  );
}
