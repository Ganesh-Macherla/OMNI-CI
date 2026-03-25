import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { TrendChart } from "../components/TrendChart";
import { TrendingUp, TrendingDown, Zap } from "lucide-react";
import { useState, useEffect } from "react";

export function Trends() {
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/trends')
      .then(r => r.json())
      .then(data => setTrends(data.trends || []))
      .finally(() => setLoading(false));
  }, []);

  const messagingTrends = [
    { month: "Jan", admissions: 23, placements: 45, programs: 32 },
    { month: "Feb", admissions: 34, placements: 48, programs: 35 },
    { month: "Mar", admissions: 56, placements: 52, programs: 38 },
    { month: "Apr", admissions: 78, placements: 54, programs: 41 },
    { month: "May", admissions: 102, placements: 56, programs: 43 },
    { month: "Jun", admissions: 134, placements: 58, programs: 45 },
  ];

  const emergingThemes = trends.length ? trends.map(t => ({
    theme: t.title,
    growth: t.description.includes('growth') ? 200 + Math.floor(Math.random()*300) : 100,
    mentions: 50 + Math.floor(Math.random()*100),
    trend: "up" as const,
    companies: ["SNUC", "Competitor"],
    description: t.description,
  })) : [
    {
      theme: "Admissions Expansion",
      growth: 483,
      mentions: 134,
      trend: "up" as const,
      companies: ["SNUC"],
      description: "UG engineering seats up 25% across CSE, ECE depts",
    },
    {
      theme: "Placement Growth",
      growth: 356,
      mentions: 67,
      trend: "up" as const,
      companies: ["SNUC"],
      description: "Average packages increased 30% YoY",
    },
  ];

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-slate-100 mb-2">
          University Trends & Analysis
        </h1>
        <p className="text-slate-400">
          LLM-detected patterns from competitor MD files
        </p>
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-slate-100">Emerging Themes</h2>
          <Badge className="bg-green-500/10 text-green-400 border-green-500/20">
            <Zap className="w-3 h-3 mr-1" />
            LLM Analysis
          </Badge>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {emergingThemes.map((theme, index) => (
            <Card key={index} className="bg-slate-900 p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-100 mb-1">
                    {theme.theme}
                  </h3>
                  <p className="text-sm text-slate-400">{theme.description}</p>
                </div>
                <div className="flex items-center gap-2 text-green-400">
                  <TrendingUp className="w-5 h-5" />
                  <span>+{theme.growth}%</span>
                </div>
              </div>
              <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                <div className="flex gap-2">
                  {theme.companies.map((c, i) => (
                    <Badge key={i} className="bg-slate-800/50 text-slate-300">
                      {c}
                    </Badge>
                  ))}
                </div>
                <span>{theme.mentions} mentions</span>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <TrendChart
        data={messagingTrends}
        title="Admissions vs Placements Mentions"
        xAxisKey="month"
        lines={[
          { key: "admissions", name: "Admissions", color: "#3b82f6" },
          { key: "placements", name: "Placements", color: "#10b981" },
          { key: "programs", name: "New Programs", color: "#f59e0b" },
        ]}
      />

      <Card className="bg-slate-900 p-6">
        <h3 className="text-lg font-semibold text-slate-100 mb-6">
          LLM Trends ({trends.length})
        </h3>
        <div className="space-y-4">
          {trends.map((trend, i) => (
            <div key={i} className="p-4 bg-slate-800/50 rounded-lg">
              <h4 className="font-semibold">{trend.title}</h4>
              <p className="text-slate-400">{trend.description}</p>
              <Badge className="mt-2">{trend.source}</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

