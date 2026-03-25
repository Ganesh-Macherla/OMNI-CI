import { Card } from "./ui/card";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface DataPoint {
  name: string;
  x: number;
  y: number;
  color: string;
}

interface ComparisonChartProps {
  data: DataPoint[];
  xLabel: string;
  yLabel: string;
  title: string;
}

export function ComparisonChart({ data, xLabel, yLabel, title }: ComparisonChartProps) {
  return (
    <Card className="bg-slate-900 border-slate-800 p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-6">{title}</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            type="number"
            dataKey="x"
            name={xLabel}
            label={{ value: xLabel, position: "bottom", fill: "#94a3b8", offset: 40 }}
            tick={{ fill: "#94a3b8" }}
            stroke="#475569"
          />
          <YAxis
            type="number"
            dataKey="y"
            name={yLabel}
            label={{ value: yLabel, angle: -90, position: "left", fill: "#94a3b8", offset: 40 }}
            tick={{ fill: "#94a3b8" }}
            stroke="#475569"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #334155",
              borderRadius: "8px",
              color: "#e2e8f0",
            }}
            cursor={{ strokeDasharray: "3 3", stroke: "#475569" }}
          />
          <Scatter data={data} fill="#8884d8">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-4 mt-4">
        {data.map((item, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-sm text-slate-400">{item.name}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
