import { createBrowserRouter } from "react-router";
import { DashboardLayout } from "./components/DashboardLayout";
import { Overview } from "./pages/Overview";
import { CompanyDossier } from "./pages/CompanyDossier";
import { Insights } from "./pages/Insights";
import { Trends } from "./pages/Trends";
import { NotFound } from "./pages/NotFound";

/**
 * Market Intelligence Dashboard Routes
 * 
 * Structure:
 * - / - Overview dashboard with key metrics and recent insights
 * - /company/:companyId - Detailed company dossier with full intelligence data
 * - /insights - All actionable insights and whitespace opportunities
 * - /trends - Market trends, emerging themes, and competitive positioning
 */
export const router = createBrowserRouter([
  {
    path: "/",
    Component: DashboardLayout,
    children: [
      { index: true, Component: Overview },
      { path: "company/:companyId", Component: CompanyDossier },
      { path: "insights", Component: Insights },
      { path: "trends", Component: Trends },
      { path: "*", Component: NotFound },
    ],
  },
]);