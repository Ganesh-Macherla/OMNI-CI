import { ExternalLink, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

interface InsightCardProps {
  insight: string;
  why: string;
  evidence?: string;
  source: string;
  sourceUrl?: string;
  action?: string;
  priority?: "high" | "medium" | "low";
  type?: "opportunity" | "threat" | "trend";
}

export function InsightCard({
  insight,
  why,
  evidence,
  source,
  sourceUrl,
  action,
  priority = "medium",
  type = "trend",
}: InsightCardProps) {
  const priorityColors = {
    high: "bg-red-500/10 text-red-400 border-red-500/20",
    medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    low: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  };

  const typeIcons = {
    opportunity: CheckCircle,
    threat: AlertCircle,
    trend: TrendingUp,
  };

  const TypeIcon = typeIcons[type];

  return (
    <Card className="bg-slate-900 border-slate-800 p-5 hover:border-slate-700 transition-colors">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-start gap-3">
          <div className="mt-0.5">
            <TypeIcon className="w-5 h-5 text-slate-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 mb-1">{insight}</h3>
            <p className="text-sm text-slate-400">{why}</p>
          </div>
        </div>
        <Badge className={priorityColors[priority]} variant="outline">
          {priority}
        </Badge>
      </div>

      {evidence && (
        <div className="mb-3 pl-8">
          <p className="text-sm text-slate-500">
            <span className="font-medium">Evidence:</span> {evidence}
          </p>
        </div>
      )}

      {action && (
        <div className="mb-3 pl-8 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <p className="text-sm text-slate-300">
            <span className="font-medium text-slate-200">Recommended Action:</span> {action}
          </p>
        </div>
      )}

      <div className="flex items-center justify-between pl-8 pt-2">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span>Source:</span>
          <span className="text-slate-400">{source}</span>
        </div>
        {sourceUrl && (
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-xs text-slate-400 hover:text-slate-200"
            onClick={() => window.open(sourceUrl, "_blank")}
          >
            View Source
            <ExternalLink className="w-3 h-3 ml-1" />
          </Button>
        )}
      </div>
    </Card>
  );
}
