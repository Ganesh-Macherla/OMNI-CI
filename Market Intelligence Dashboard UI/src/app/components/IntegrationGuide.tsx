import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Code, Database, Zap, Search, Bell } from "lucide-react";
import { useScrape } from "../hooks/useMarketIntel";

export function IntegrationGuide() {
  const { scrape, loading, error, result } = useScrape();

  const integrationSteps = [
    {
      icon: Search,
      title: "Data Collection",
      description: "Web scrapers collect university MD files (admissions, placements)",
      technologies: ["crawl4ai", "Playwright"],
    },
    {
      icon: Database,
      title: "Data Storage",
      description: "MD files stored for LLM analysis",
      technologies: ["File system"],
    },
    {
      icon: Zap,
      title: "LLM Processing",
      description: "Cerebras LLM generates insights on admissions/placements",
      technologies: ["Python", "FastAPI", "Cerebras API"],
    },
    {
      icon: Code,
      title: "API Layer",
      description: "REST APIs serve LLM insights to frontend",
      technologies: ["FastAPI"],
    },
    {
      icon: Bell,
      title: "Competitor Scraping",
      description: "Add URL → auto crawl → LLM insights",
      technologies: ["crawl4ai"],
    },
  ];

  const handleScrape = () => {
    const urlInput = document.getElementById('scrapeUrl') as HTMLInputElement;
    const companyInput = document.getElementById('companyName') as HTMLInputElement;
    const url = urlInput?.value;
    const company = companyInput?.value;
    if (url && company) {
      scrape(url, company);
    }
  };

  return (
    <Card className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20 p-6 space-y-6">
      <div className="flex items-start gap-4 mb-6">
        <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
          <Database className="w-6 h-6 text-blue-400" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-slate-100 mb-2">
            Backend Integration Active
          </h3>
          <p className="text-slate-400">
            Fully connected to real backend APIs. LLM analyzes scraped MD files.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {integrationSteps.map((step, index) => (
          <div key={index} className="flex gap-4 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center">
                <step.icon className="w-5 h-5 text-slate-400" />
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold text-slate-500">STEP {index + 1}</span>
                <h4 className="font-semibold text-slate-100">{step.title}</h4>
              </div>
              <p className="text-sm text-slate-400 mb-3">{step.description}</p>
              <div className="flex flex-wrap gap-2">
                {step.technologies.map((tech, idx) => (
                  <Badge
                    key={idx}
                    variant="outline"
                    className="bg-slate-800/50 text-slate-300 border-slate-700"
                  >
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
        <h4 className="font-semibold text-slate-100 mb-2">Active API Endpoints</h4>
        <div className="space-y-2 text-sm font-mono">
          <div className="flex gap-2">
            <Badge className="bg-green-500/10 text-green-400 border-green-500/20">GET</Badge>
            <code className="text-slate-300">/api/companies</code>
          </div>
          <div className="flex gap-2">
            <Badge className="bg-green-500/10 text-green-400 border-green-500/20">GET</Badge>
            <code className="text-slate-300">/api/insights</code>
          </div>
          <div className="flex gap-2">
            <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/20">POST</Badge>
            <code className="text-slate-300">/api/scrape</code>
          </div>
        </div>
      </div>

      {/* Competitor Scrape Form */}
      <Card className="bg-gradient-to-br from-emerald-500/10 to-green-500/10 border-emerald-500/20 p-6">
        <h3 className="text-xl font-semibold text-slate-100 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          Add Competitor University
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <Input
            id="scrapeUrl"
            type="url"
            placeholder="https://competitor-uni.edu.in"
            className="col-span-2"
          />
          <Input
            id="companyName"
            type="text"
            placeholder="CompetitorUni"
          />
        </div>
        <Button onClick={handleScrape} disabled={loading} className="w-full">
          {loading ? "Scraping..." : "🚀 Start Scraping"}
        </Button>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
        {result && (
          <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
            <p className="text-emerald-400 font-medium">Success! {result.files_saved} files scraped for {result.company}</p>
            <p className="text-xs text-emerald-300 mt-1">Refresh dashboard for new insights</p>
          </div>
        )}
        <p className="text-xs text-emerald-400 mt-3 text-center">
          Crawls site → saves MD → LLM analyzes automatically
        </p>
      </Card>
    </Card>
  );
}

