import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { ArrowRight, Calendar } from "lucide-react";

interface TimelineEvent {
  date: string;
  type: "pricing" | "feature" | "messaging" | "other";
  before: string;
  after: string;
  impact?: string;
}

interface ChangeTimelineProps {
  events: TimelineEvent[];
  title?: string;
}

export function ChangeTimeline({ events, title = "Change Detection Timeline" }: ChangeTimelineProps) {
  const typeColors = {
    pricing: "bg-green-500/10 text-green-400 border-green-500/20",
    feature: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    messaging: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    other: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  };

  return (
    <Card className="bg-slate-900 border-slate-800 p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-6">{title}</h3>
      <div className="space-y-6">
        {events.map((event, index) => (
          <div key={index} className="relative">
            {index !== events.length - 1 && (
              <div className="absolute left-4 top-12 bottom-0 w-px bg-slate-800" />
            )}
            <div className="flex gap-4">
              <div className="relative flex-shrink-0">
                <div className="w-8 h-8 bg-slate-800 border-2 border-slate-700 rounded-full flex items-center justify-center">
                  <Calendar className="w-4 h-4 text-slate-400" />
                </div>
              </div>
              <div className="flex-1 pb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm text-slate-400">{event.date}</span>
                  <Badge className={typeColors[event.type]} variant="outline">
                    {event.type}
                  </Badge>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <p className="text-xs text-slate-500 mb-1">Before</p>
                      <p className="text-sm text-slate-300">{event.before}</p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-600 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-xs text-slate-500 mb-1">After</p>
                      <p className="text-sm text-slate-100 font-medium">{event.after}</p>
                    </div>
                  </div>
                  {event.impact && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <p className="text-xs text-slate-400">
                        <span className="font-medium">Impact:</span> {event.impact}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
