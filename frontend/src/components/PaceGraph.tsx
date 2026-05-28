import { useRef, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { useTelemetryStore } from "../store/telemetryStore";

interface LapEntry {
  lap: number;
  time: number;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  const whole = Math.floor(s);
  const millis = Math.round((s - whole) * 1000);
  return `${m}:${String(whole).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
}

export default function PaceGraph() {
  const data = useTelemetryStore((s) => s.data);
  const historyRef = useRef<LapEntry[]>([]);
  const lastLapRef = useRef<number>(-1);

  useEffect(() => {
    if (!data?.graphics) return;

    const completed = data.graphics.completed_laps;
    if (completed > lastLapRef.current && data.graphics.lap_time > 0) {
      historyRef.current = [
        ...historyRef.current,
        { lap: completed, time: data.graphics.lap_time },
      ];
      lastLapRef.current = completed;
    }
  }, [data]);

  const laps = historyRef.current;

  if (laps.length === 0) {
    return (
      <div className="bg-rc-surface rounded-lg p-4 h-64 flex items-center justify-center">
        <p className="text-rc-muted font-mono text-sm">Waiting for lap data...</p>
      </div>
    );
  }

  const bestLap = Math.min(...laps.map((l) => l.time));
  const lastLap = laps[laps.length - 1].time;
  const avgLap =
    laps.reduce((sum, l) => sum + l.time, 0) / laps.length;

  return (
    <div className="bg-rc-surface rounded-lg p-4">
      <h3 className="text-rc-text font-semibold mb-2">Lap Times</h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={laps}
            margin={{ top: 8, right: 16, left: 0, bottom: 8 }}
          >
            <CartesianGrid stroke="#2a2d3a" strokeDasharray="3 3" />
            <XAxis
              dataKey="lap"
              stroke="#8b8fa3"
              tick={{ fill: "#8b8fa3", fontSize: 12 }}
              tickLine={false}
              label={{
                value: "Lap",
                position: "insideBottomRight",
                offset: -4,
                fill: "#8b8fa3",
                fontSize: 12,
              }}
            />
            <YAxis
              stroke="#8b8fa3"
              tick={{ fill: "#8b8fa3", fontSize: 12 }}
              tickLine={false}
              tickFormatter={(v: number) => v.toFixed(1)}
              label={{
                value: "Time (s)",
                angle: -90,
                position: "insideLeft",
                fill: "#8b8fa3",
                fontSize: 12,
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1a1d27",
                border: "1px solid #2a2d3a",
                borderRadius: "6px",
                color: "#e0e0e0",
                fontSize: 13,
              }}
              formatter={(value) => [formatTime(value as number), "Lap Time"]}
              labelFormatter={(label) => `Lap ${label}`}
            />
            <ReferenceLine
              y={bestLap}
              stroke="#22c55e"
              strokeDasharray="4 4"
              label={{
                value: "Best",
                fill: "#22c55e",
                fontSize: 11,
                position: "right",
              }}
            />
            <Line
              type="monotone"
              dataKey="time"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3, fill: "#3b82f6", strokeWidth: 0 }}
              activeDot={{ r: 5, fill: "#3b82f6", strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-4 text-center font-mono text-sm">
        <div>
          <p className="text-rc-muted text-xs">Best</p>
          <p className="text-rc-accent">{formatTime(bestLap)}</p>
        </div>
        <div>
          <p className="text-rc-muted text-xs">Last</p>
          <p className="text-rc-text">{formatTime(lastLap)}</p>
        </div>
        <div>
          <p className="text-rc-muted text-xs">Average</p>
          <p className="text-rc-text">{formatTime(avgLap)}</p>
        </div>
      </div>
    </div>
  );
}
