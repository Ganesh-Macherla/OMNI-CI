import { useNavigate } from "react-router";
import { Button } from "../components/ui/button";
import { Home, Search } from "lucide-react";

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] p-8">
      <div className="text-center max-w-md">
        <div className="w-24 h-24 bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Search className="w-12 h-12 text-slate-600" />
        </div>
        <h1 className="text-4xl font-semibold text-slate-100 mb-3">
          Page Not Found
        </h1>
        <p className="text-slate-400 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Button
          onClick={() => navigate("/")}
          className="gap-2"
        >
          <Home className="w-4 h-4" />
          Back to Dashboard
        </Button>
      </div>
    </div>
  );
}
