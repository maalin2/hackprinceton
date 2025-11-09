"use client";

import {
  LineChart,
  Line,
  Area,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import { Activity } from "lucide-react";

// Mock data for trading volume by day of the week
const weeklyData = [
  { day: "Mon", volume: 4200 },
  { day: "Tue", volume: 5800 },
  { day: "Wed", volume: 7200 },
  { day: "Thu", volume: 6100 },
  { day: "Fri", volume: 8400 },
  { day: "Sat", volume: 3200 },
  { day: "Sun", volume: 2800 },
];

export function WeeklyTradingChart() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-green-600 dark:text-green-400" />
          <CardTitle>Weekly Trading Volume</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <ComposedChart data={weeklyData}>
            <defs>
              <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgb(22, 163, 74)" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="rgb(22, 163, 74)" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" opacity={0.3} />
            <XAxis
              dataKey="day"
              className="text-xs"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
              tickLine={false}
            />
            <YAxis
              className="text-xs"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
              tickFormatter={(value) => formatCurrency(value, 0)}
              tickLine={false}
              width={60}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              formatter={(value: number) => [formatCurrency(value), "Volume"]}
            />
            <Area
              type="monotone"
              dataKey="volume"
              fill="url(#colorVolume)"
              stroke="none"
              animationDuration={1000}
            />
            <Line
              type="monotone"
              dataKey="volume"
              stroke="rgb(22, 163, 74)"
              strokeWidth={3}
              dot={{ fill: "rgb(22, 163, 74)", strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
              animationDuration={1000}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
