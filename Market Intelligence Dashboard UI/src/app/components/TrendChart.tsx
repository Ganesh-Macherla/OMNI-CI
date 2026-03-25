import { Card } from "./ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface TrendChartProps {
  data: any[];
  lines: {
    key: string;
    name: string;
    color: string;
  }[];
  title: string;
  xAxisKey: string;
}

export function TrendChart({ data, lines, title, xAxisKey }: TrendChartProps) {
  return (
    <Card className="bg-slate-900 border-slate-800 p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-6">{title}</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey={xAxisKey}
            tick={{ fill: "#94a3b8" }}
            stroke="#475569"
          />
          <YAxis
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
          />
          <Legend
            wrapperStyle={{ color: "#94a3b8" }}
            iconType="line"
          />
          {lines.map((line) => (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              name={line.name}
              stroke={line.color}
              strokeWidth={2}
              dot={{ fill: line.color, r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
