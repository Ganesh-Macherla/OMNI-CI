import { Outlet, NavLink } from "react-router";
import { 
  LayoutDashboard, 
  Building2, 
  TrendingUp, 
  Lightbulb, 
  Search,
  Bell,
  Settings,
  ChevronDown,
  Plus
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { NewAnalysis } from "./NewAnalysis";
import { useEffect, useState, useTransition } from "react";

export function DashboardLayout() {
  const [companies, setCompanies] = useState<string[]>([]);
  const [isPending, startTransition] = useTransition();

  const refreshCompanies = () => {
    fetch('/api/companies')
      .then(r => r.json())
      .then(data => {
        const names = data.companies?.map((c: any) => c.name || c.id) || ["Shiv Nadar University Chennai"];
        setCompanies(names.slice(0,3));
      })
      .catch(() => {
        setCompanies(["Shiv Nadar University Chennai", "Competitor University", "Regional Eng College"]);
      });
  };

  useEffect(() => {
    refreshCompanies();
  }, []);



  const navItems = [
    { path: "/", label: "Overview", icon: LayoutDashboard },
    { path: "/insights", label: "Insights", icon: Lightbulb },
    { path: "/trends", label: "Trends", icon: TrendingUp },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-lg">University Intel</h1>
              <p className="text-xs text-slate-400">LLM Analysis Engine</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  isActive
                    ? "bg-slate-800 text-white"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}

          <div className="pt-6">
            <p className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Tracked Universities
            </p>
            <div className="space-y-1">
              {companies.map((company) => (
                <NavLink
                  key={company}
                  to={`/companies/${company.toLowerCase().replace(/\s+/g, '-')}`}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm truncate ${
                      isActive
                        ? "bg-slate-800 text-white"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                    }`
                  }
                >
                  <Building2 className="w-4 h-4 flex-shrink-0" />
                  <span>{company}</span>
                </NavLink>
              ))}
              <NewAnalysis 
                triggerButton={
                  <Button variant="ghost" className="w-full justify-start text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 px-3 py-2 text-sm h-auto">
                    <Plus className="w-4 h-4 mr-3 h-4 flex-shrink-0" />
                    <span>Add University</span>
                  </Button>
                }
              />
            </div>
          </div>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 cursor-pointer transition-colors">
            <Avatar className="w-8 h-8">
              <AvatarFallback className="bg-slate-700 text-slate-200">
                NS
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">N Sivakumar</p>
              <p className="text-xs text-slate-400 truncate">user@snuc.edu.in</p>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
          <div className="flex-1 max-w-xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search universities, depts, admissions..."
                className="pl-10 bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-200">
              <Bell className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-200">
              <Settings className="w-5 h-5" />
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-auto bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

