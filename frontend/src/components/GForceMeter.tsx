import { useTelemetryStore } from "../store/telemetryStore";

export default function GForceMeter() {
  const data = useTelemetryStore((s) => s.data);
  const ax = data?.physics?.acceleration_x ?? 0; // lateral (m/s²)
  const ay = data?.physics?.acceleration_y ?? 0; // longitudinal
  const gForce = data?.physics?.g_force ?? 0;

  // Convert to Gs (1g = 9.81 m/s²), clamp to display range
  const lateralG = Math.max(-3, Math.min(3, ax / 9.81)); // cornering
  const longG = Math.max(-3, Math.min(3, ay / 9.81)); // braking/accel

  // Circle center at 50%, scale: 3G = 50% of radius
  const dotX = 50 + (lateralG / 3) * 45;
  const dotY = 50 - (longG / 3) * 45; // invert Y: positive G = braking = up

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold">
          G-Force
        </h2>
        <span className="text-lg font-mono font-bold text-rc-accent">
          {data ? gForce.toFixed(1) : "--"} G
        </span>
      </div>

      <div className="relative w-full aspect-square max-w-[200px] mx-auto">
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Outer circle */}
          <circle cx="50" cy="50" r="48" fill="none" stroke="#334155" strokeWidth="1" />
          <circle cx="50" cy="50" r="32" fill="none" stroke="#1e293b" strokeWidth="1" />
          <circle cx="50" cy="50" r="16" fill="none" stroke="#1e293b" strokeWidth="0.5" />

          {/* Crosshairs */}
          <line x1="50" y1="2" x2="50" y2="98" stroke="#1e293b" strokeWidth="0.5" />
          <line x1="2" y1="50" x2="98" y2="50" stroke="#1e293b" strokeWidth="0.5" />

          {/* G-force dot with trail */}
          <circle
            cx={dotX}
            cy={dotY}
            r="4"
            fill="#22d3ee"
            stroke="#0891b2"
            strokeWidth="1"
            className="transition-all duration-75 ease-linear"
          />
          <line
            x1="50"
            y1="50"
            x2={dotX}
            y2={dotY}
            stroke="#22d3ee"
            strokeWidth="1"
            opacity="0.5"
            className="transition-all duration-75 ease-linear"
          />
        </svg>

        {/* Labels */}
        <span className="absolute top-1 left-1/2 -translate-x-1/2 text-[10px] text-rc-muted font-mono">
          BRK
        </span>
        <span className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[10px] text-rc-muted font-mono">
          ACC
        </span>
        <span className="absolute left-1 top-1/2 -translate-y-1/2 text-[10px] text-rc-muted font-mono">
          L
        </span>
        <span className="absolute right-1 top-1/2 -translate-y-1/2 text-[10px] text-rc-muted font-mono">
          R
        </span>
      </div>

      {/* Lateral + longitudinal bars */}
      <div className="grid grid-cols-2 gap-2">
        <div className="flex flex-col gap-0.5">
          <div className="flex justify-between">
            <span className="text-[10px] text-rc-muted font-mono uppercase">
              Lateral
            </span>
            <span className="text-[10px] font-mono text-rc-text">
              {lateralG.toFixed(2)}g
            </span>
          </div>
          <div className="w-full h-1.5 bg-rc-bg rounded overflow-hidden flex">
            <div className="w-1/2 h-full flex justify-end">
              <div
                className="h-full bg-cyan-500 transition-all duration-75"
                style={{
                  width: `${Math.max(0, -lateralG) / 3 * 50}%`,
                }}
              />
            </div>
            <div className="w-1/2 h-full">
              <div
                className="h-full bg-cyan-500 transition-all duration-75"
                style={{
                  width: `${Math.max(0, lateralG) / 3 * 50}%`,
                }}
              />
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-0.5">
          <div className="flex justify-between">
            <span className="text-[10px] text-rc-muted font-mono uppercase">Long</span>
            <span className="text-[10px] font-mono text-rc-text">
              {longG.toFixed(2)}g
            </span>
          </div>
          <div className="w-full h-1.5 bg-rc-bg rounded overflow-hidden flex">
            <div className="w-1/2 h-full flex justify-end">
              <div
                className="h-full bg-purple-500 transition-all duration-75"
                style={{
                  width: `${Math.max(0, -longG) / 3 * 50}%`,
                }}
              />
            </div>
            <div className="w-1/2 h-full">
              <div
                className="h-full bg-purple-500 transition-all duration-75"
                style={{
                  width: `${Math.max(0, longG) / 3 * 50}%`,
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
