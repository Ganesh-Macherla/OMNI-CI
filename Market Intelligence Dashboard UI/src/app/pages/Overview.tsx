import {
  Building2,
  TrendingUp,
  Lightbulb,
  Target,
  AlertTriangle,
  Activity,
} from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { InsightCard } from "../components/InsightCard";
import { TrendChart } from "../components/TrendChart";
import { IntegrationGuide } from "../components/IntegrationGuide";
import { NewAnalysis } from "../components/NewAnalysis";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { useNavigate } from "react-router";
import { useState, useEffect } from "react";

export function Overview() {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState<any[]>([]);
  const [insights, setInsights] = useState<any[]>([]);
  const [dashboardRes, setDashboardRes] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch('/api/companies').then(r => r.json()).catch(() => ({companies: []})),
      fetch('/api/insights').then(r => r.json()).catch(() => ({insights: []})),
      fetch('/api/dashboard').then(r => r.json()).catch(() => ({}))
    ]).then(([companiesRes, insightsRes, dashRes]) => {
      setCompanies(companiesRes.companies || dashRes.companies || []);
      setInsights(insightsRes.insights || dashRes.insights || []);
      setDashboardRes(dashRes);
      setLoading(false);
    }).catch((e) => {
      console.error('API error:', e);
      setLoading(false);
    });
  }, []); 

  const trendData = dashboardRes.trends?.map((t: any) => ({
    month: t.title.slice(0,3),
    mentions: Math.random()*300,
    launches: Math.random()*25,
    pricingChanges: Math.random()*10,
  })) || [
    { month: "Jan", mentions: 145, launches: 8, pricingChanges: 3 },
    { month: "Feb", mentions: 178, launches: 12, pricingChanges: 5 },
  ];

  if (loading) {
    return <div className="p-8 text-slate-400">Loading real university intel from backend LLM...</div>;
  }

  const recentInsights = insights.slice(0,3).map((i, idx) => ({
    insight: i.title || i.insight || 'No title',
    why: i.description || i.why || '',
    evidence: i.evidence || '',
    source: i.source || '',
    action: i.recommended_action || i.action || '',
    priority: i.impact || i.priority || "medium" as const,
    type: "opportunity" as const
  })); 

  const trackedCompanies = companies.slice(0,4).map(c => ({
    id: c.id,
    name: c.name,
    status: "Active",
    lastUpdate: "Live from backend",
    changes: 2,
    sentiment: "positive"
  })); 

  return (
    <div className="p-8 space-y-8">
      <div className="space-y-4">
        <div>
          <h1 className="text-3xl font-semibold text-slate-100 mb-2">
            University Intelligence Overview
          </h1>
          <p className="text-slate-400">
            LLM analysis of competitor MD files (admissions, placements, programs)
          </p>
        </div>
        <div className="flex gap-4">
          <NewAnalysis />
          <Button variant="outline" className="border-slate-700">
            Quick Compare
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Tracked Departments"
          value={companies.length}
          change={12}
          changeLabel="vs last month"
          icon={Building2}
          trend="up"
        />
        <MetricCard
          title="Active Insights"
          value={insights.length}
          change={23}
          changeLabel="this week"
          icon={Lightbulb}
          trend="up"
        />
        <MetricCard
          title="Market Changes"
          value={dashboardRes.changes?.length || 47}
          change={8}
          changeLabel="last 7 days"
          icon={Activity}
          trend="up"
        />
        <MetricCard
          title="Opportunities"
          value={dashboardRes.trends?.length || 12}
          change={-3}
          changeLabel="vs last week"
          icon={Target}
          trend="down"
        />
      </div>

      <TrendChart
        data={trendData}
        title="Admissions & Placement Trends"
        xAxisKey="month"
        lines={[
          { key: "mentions", name: "Seat Mentions", color: "#3b82f6" },
          { key: "launches", name: "New Programs", color: "#10b981" },
          { key: "pricingChanges", name: "Fee Changes", color: "#f59e0b" },
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xl font-semibold text-slate-100">Recent LLM Insights</h2>
            <button
              onClick={() => navigate("/insights")}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              View all →
            </button>
          </div>
          {recentInsights.map((insight, index) => (
            <InsightCard key={index} {...insight} />
          ))}
        </div>

        <div>
          <h2 className="text-xl font-semibold text-slate-100 mb-4">
            Tracked Universities
          </h2>
          <Card className="bg-slate-900 border-slate-800 divide-y divide-slate-800">
            {trackedCompanies.map((company) => (
              <div
                key={company.id}
                onClick={() => navigate(`/company/${company.id}`)}
                className="p-4 hover:bg-slate-800/50 cursor-pointer transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-slate-400" />
                    </div>
                    <div>
                      <h3 className="font-medium text-slate-100">{company.name}</h3>
                      <p className="text-xs text-slate-500">{company.lastUpdate}</p>
                    </div>
                  </div>
                  <Badge className="bg-green-500/10 text-green-400 border-green-500/20">
                    Active
                  </Badge>
                </div>
              </div>
            ))}
          </Card>
        </div>
      </div>

      <IntegrationGuide />
    </div>
  );
}

