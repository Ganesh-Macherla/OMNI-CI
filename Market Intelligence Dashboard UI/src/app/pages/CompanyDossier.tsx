import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  Building2,
  Globe,
  Users,
  TrendingUp,
  MessageSquare,
  Star,
  ExternalLink,
  Package,
  ChevronDown,
  BarChart3
} from "lucide-react";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { ChangeTimeline } from "../components/ChangeTimeline";
import { Button } from "../components/ui/button";
import { Progress } from "../components/ui/progress";
import { useCompanies } from "../hooks/useMarketIntel";

export function CompanyDossier() {
  const { companyId } = useParams();
  const [company, setCompany] = useState<any>(null);
  const [competitorId, setCompetitorId] = useState<string>('');
  const [competitor, setCompetitor] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { companies } = useCompanies();

  useEffect(() => {
    if (companyId) {
      fetch(`/api/companies/${companyId}`)
        .then(r => r.json())
        .then(data => setCompany(data.company))
        .catch(() => {
          setCompany({
            id: companyId || "snuc",
            name: "Shiv Nadar Univ Chennai",
            overview: "Private engineering university with CSE, ECE, Mechanical depts.",
            dossier: "24 MD files analyzed (admissions, placements, faculty)",
            website: "https://www.snuchennai.edu.in"
          });
        })
        .finally(() => setLoading(false));
    }
  }, [companyId]);

  useEffect(() => {
    if (competitorId && competitorId !== companyId) {
      fetch(`/api/companies/${competitorId}`)
        .then(r => r.json())
        .then(data => setCompetitor(data.company))
        .catch(() => setCompetitor(null));
    } else {
      setCompetitor(null);
    }
  }, [competitorId, companyId]);

  if (loading) {
    return <div className="p-8 text-slate-400">Loading university dossier from backend...</div>;
  }

  const handleOpenWebsite = () => {
    window.open(company.website || 'https://www.snuchennai.edu.in', '_blank');
  };

  const timelineEvents = [
    {
      date: "Apr 2026",
      type: "feature" as const,
      before: "120 CSE seats",
      after: "144 CSE seats (+20%)",
      impact: "Expanded flagship program",
    },
    {
      date: "Mar 2026",
      type: "pricing" as const,
      before: "Avg 8 LPA placements",
      after: "Avg 10.5 LPA (+31%)",
      impact: "Placement growth",
    },
    {
      date: "Feb 2026",
      type: "messaging" as const,
      before: "No Economics",
      after: "B.Sc Economics launched",
      impact: "Commerce diversification",
    },
  ];

  const features = [
    { name: "CSE Department", status: "Active", lastUpdated: "Apr 2026" },
    { name: "ECE Department", status: "Active", lastUpdated: "Mar 2026" },
    { name: "Mechanical Eng", status: "Active", lastUpdated: "Feb 2026" },
    { name: "B.Sc Economics", status: "New", lastUpdated: "Jan 2026" },
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Header with Competitor Selector */}
      <div className="space-y-6">
        <div className="flex items-start justify-between gap-6">
          <div className="flex items-start gap-4 flex-1">
            <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
              <Building2 className="w-10 h-10 text-white" />
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-semibold text-slate-100 mb-2">
                {company.name}
              </h1>
              <p className="text-slate-400 mb-4">{company.overview}</p>
              <div className="flex items-center gap-4 text-sm text-slate-400">
                <div className="flex items-center gap-1">
                  <Globe className="w-4 h-4" />
                  <span>{company.website || 'https://www.snuchennai.edu.in'}</span>
                </div>
                <Badge className="bg-green-500/10 text-green-400 border-green-500/20">
                  LLM Dossier
                </Badge>
              </div>
            </div>
          </div>
          
          {/* Competitor Selector */}
          <div className="flex flex-col items-end gap-2">
            <Select value={competitorId} onValueChange={setCompetitorId}>
              <SelectTrigger className="w-[220px] h-12 bg-slate-900 border-slate-700">
                <SelectValue placeholder="Compare with..." />
              </SelectTrigger>
              <SelectContent>
                {companies
                  ?.filter(c => c.id !== companyId)
                  ?.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.name}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
            
            <Button variant="outline" className="border-slate-700 w-[220px]" onClick={handleOpenWebsite}>
              <ExternalLink className="w-4 h-4 mr-2" />
              {company.website ? 'Website' : 'SNUC Site'}
            </Button>
          </div>
        </div>

        {/* Comparison Cards if competitor selected */}
        {competitor && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-slate-900/50 border-slate-800 p-6 relative">
              <Badge className="absolute -top-3 left-4 bg-emerald-500 text-white px-3 py-1 rounded-full">
                Primary: {company.name}
              </Badge>
              <div className="space-y-2">
                <p className="text-sm text-slate-400">Files Analyzed</p>
                <p className="text-2xl font-semibold">{company.dossier?.match(/\\d+/)?.[0] || '24'}</p>
              </div>
            </Card>
            <Card className="bg-slate-900/50 border-slate-800 p-6 relative">
              <Badge className="absolute -top-3 left-4 bg-orange-500 text-white px-3 py-1 rounded-full">
                Competitor: {competitor.name}
              </Badge>
              <div className="space-y-2">
                <p className="text-sm text-slate-400">Files Analyzed</p>
                <p className="text-2xl font-semibold">{competitor.dossier?.match(/\\d+/)?.[0] || 'N/A'}</p>
              </div>
            </Card>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-slate-900 p-6">
          <p className="text-sm text-slate-400 mb-2">Analysis Summary</p>
          <p className="text-2xl font-semibold">{company.dossier}</p>
        </Card>
      </div>

      <Tabs defaultValue="changes">
        <TabsList className="bg-slate-900">
          <TabsTrigger value="changes">Changes</TabsTrigger>
          <TabsTrigger value="programs">Programs</TabsTrigger>
        </TabsList>

        <TabsContent value="changes" className="space-y-6">
          <ChangeTimeline events={timelineEvents} />
        </TabsContent>

        <TabsContent value="programs">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((f, i) => (
              <Card key={i} className="bg-slate-900 p-6">
                <div className="flex justify-between">
                  <div>
                    <h4 className="font-semibold">{f.name}</h4>
                    <p className="text-sm text-slate-400">{f.lastUpdated}</p>
                  </div>
                  <Badge variant={f.status === "New" ? "default" : "outline"}>
                    {f.status}
                  </Badge>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
