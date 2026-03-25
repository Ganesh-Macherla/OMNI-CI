// SNU University-themed mock data matching backend LLM output (dev fallback only)
// Live app uses real /api/* → backend LLM analysis of md_files

export const companies = [
  {
    id: "snuc",
    name: "Shiv Nadar University Chennai",
    industry: "Higher Education",
    segment: "Private Engineering & Commerce",
    geography: "Chennai, Tamil Nadu",
    website: "snuc.edu.in",
    founded: "2022",
    employees: "250+",
  },
  {
    id: "competitor",
    name: "Competitor Engineering University",
    industry: "Higher Education",
    segment: "Engineering & Technology",
    geography: "South India",
    website: "competitor.edu.in",
    founded: "2015",
    employees: "800+",
  },
];

export const insights = [
  {
    id: "1",
    insight: "Competitor expanded UG admissions by 25% for CSE",
    why: "Increased demand for Computer Science programs across region",
    evidence: "New seats announced in admissions.md, UG-admissions.md",
    source: "scraped_md/admissions.md (Apr 2026)",
    sourceUrl: "#",
    action: "Benchmark CSE intake vs regional peers",
    priority: "high" as const,
    type: "threat" as const,
    createdAt: "2026-04-15",
  },
  {
    id: "2",
    insight: "New B.Sc Economics program launched",
    why: "Shift toward interdisciplinary commerce programs",
    evidence: "b-sc-economics.md, programs.md updates",
    source: "backend/data/md_files/programs.md",
    sourceUrl: "#",
    action: "Evaluate Economics program competitiveness",
    priority: "medium" as const,
    type: "opportunity" as const,
    createdAt: "2026-04-10",
  },
];

export const trends = [
  {
    id: "1",
    name: "Admissions Expansion",
    growth: 28,
    mentions: 45,
    trend: "up" as const,
    companies: ["SNUC", "Competitor"],
    description: "UG/PG seats increased across engineering departments",
  },
  {
    id: "2",
    name: "Placement Improvements",
    growth: 15,
    mentions: 32,
    trend: "up" as const,
    companies: ["SNUC"],
    description: "Average package and placement % trending upward",
  },
];

// Export type definitions for TypeScript (matching backend Pydantic)
export type Company = typeof companies[0];
export type Insight = typeof insights[0];
export type Trend = typeof trends[0];

