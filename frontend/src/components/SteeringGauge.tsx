import { useTelemetryStore } from "../store/telemetryStore";

export default function SteeringGauge() {
  const data = useTelemetryStore((s) => s.data);
  const steer = data?.physics?.steering ?? 0;
  // steer is -1 (full left) to 1 (full right), ~±450 degrees visual range
  const rotationDeg = steer * 180; // ±180 degrees visual

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4 flex flex-col items-center gap-2">
      <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold self-start">
        Steering
      </h2>

      <div className="relative w-32 h-32 flex items-center justify-center">
        {/* Wheel background ring */}
        <svg
          viewBox="0 0 120 120"
          className="w-full h-full transition-transform duration-75 ease-linear"
          style={{ transform: `rotate(${rotationDeg}deg)` }}
        >
          {/* Outer ring */}
          <circle
            cx="60"
            cy="60"
            r="55"
            fill="none"
            stroke="#334155"
            strokeWidth="6"
          />
          {/* Inner ring */}
          <circle
            cx="60"
            cy="60"
            r="40"
            fill="none"
            stroke="#1e293b"
            strokeWidth="3"
          />
          {/* Spokes */}
          <line x1="60" y1="5" x2="60" y2="20" stroke="#475569" strokeWidth="4" />
          <line x1="60" y1="100" x2="60" y2="115" stroke="#475569" strokeWidth="4" />
          <line x1="5" y1="60" x2="20" y2="60" stroke="#475569" strokeWidth="4" />
          <line x1="100" y1="60" x2="115" y2="60" stroke="#475569" strokeWidth="4" />
          {/* Center hub */}
          <circle cx="60" cy="60" r="10" fill="#64748b" />
          {/* Top center marker */}
          <rect x="57" y="8" width="6" height="12" rx="2" fill="#f87171" />
        </svg>

        {/* Fixed center dot (doesn't rotate with wheel) */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span className="text-xs font-mono font-bold text-rc-text">
            {data ? `${(steer * 180).toFixed(0)}°` : "--"}
          </span>
        </div>
      </div>

      {/* Steering input bar */}
      <div className="w-full h-2 bg-rc-bg rounded overflow-hidden flex">
        <div
          className="h-full bg-rc-accent transition-all duration-75 ease-linear"
          style={{
            width: `${Math.abs(steer) * 50}%`,
            marginLeft: steer < 0 ? `${50 - Math.abs(steer) * 50}%` : "50%",
          }}
        />
        <div className="w-0.5 h-full bg-white/30 absolute left-1/2" />
      </div>
    </div>
  );
}
