import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { Card } from "./ui/card";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: LucideIcon;
  trend?: "up" | "down" | "neutral";
}

export function MetricCard({
  title,
  value,
  change,
  changeLabel,
  icon: Icon,
  trend = "neutral",
}: MetricCardProps) {
  return (
    <Card className="bg-slate-900 border-slate-800 p-6 hover:border-slate-700 transition-colors">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400 mb-2">{title}</p>
          <p className="text-3xl font-semibold text-slate-100 mb-2">{value}</p>
          {change !== undefined && (
            <div className="flex items-center gap-2">
              {trend === "up" && (
                <div className="flex items-center gap-1 text-green-400">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-sm font-medium">+{change}%</span>
                </div>
              )}
              {trend === "down" && (
                <div className="flex items-center gap-1 text-red-400">
                  <TrendingDown className="w-4 h-4" />
                  <span className="text-sm font-medium">{change}%</span>
                </div>
              )}
              {trend === "neutral" && (
                <div className="flex items-center gap-1 text-slate-400">
                  <span className="text-sm font-medium">{change}%</span>
                </div>
              )}
              {changeLabel && (
                <span className="text-xs text-slate-500">{changeLabel}</span>
              )}
            </div>
          )}
        </div>
        <div className="w-12 h-12 bg-slate-800 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-slate-400" />
        </div>
      </div>
    </Card>
  );
}
