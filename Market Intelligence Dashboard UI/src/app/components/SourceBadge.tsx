import { ExternalLink } from "lucide-react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

interface SourceBadgeProps {
  source: string;
  url?: string;
  date?: string;
}

export function SourceBadge({ source, url, date }: SourceBadgeProps) {
  if (url) {
    return (
      <Button
        variant="ghost"
        size="sm"
        className="h-auto px-2 py-1 text-xs text-slate-400 hover:text-slate-200"
        onClick={() => window.open(url, "_blank")}
      >
        {source}
        {date && <span className="ml-1 text-slate-500">({date})</span>}
        <ExternalLink className="w-3 h-3 ml-1" />
      </Button>
    );
  }

  return (
    <Badge variant="outline" className="bg-slate-800/50 text-slate-400 border-slate-700">
      {source}
      {date && <span className="ml-1 text-slate-500">({date})</span>}
    </Badge>
  );
}
