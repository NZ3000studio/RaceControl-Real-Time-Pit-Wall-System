import { useTelemetryStore } from "../store/telemetryStore";

const WHEEL_LABELS = ["FL", "FR", "RL", "RR"] as const;

export default function BrakePanel() {
  const data = useTelemetryStore((s) => s.data);
  const wheels = data?.physics?.wheels;
  const brakeBias = data?.physics?.brake_bias ?? 0;

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4">
      <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold mb-3">
        Brakes
      </h2>

      {/* Brake pressure per wheel */}
      <div className="grid grid-cols-4 gap-1.5 mb-3">
        {WHEEL_LABELS.map((label, i) => {
          const p = wheels?.[i]?.brake_pressure ?? null;
          const pct = Math.min(p ?? 0, 100);
          return (
            <div key={label} className="flex flex-col items-center gap-0.5">
              <span className="text-[10px] font-mono text-rc-muted">
                {label}
              </span>
              <div className="w-full h-10 bg-rc-bg rounded overflow-hidden flex flex-col-reverse">
                <div
                  className="w-full bg-red-500 transition-all duration-75"
                  style={{ height: `${pct}%` }}
                />
              </div>
              <span className="text-[10px] font-mono text-rc-text">
                {p !== null ? `${p.toFixed(0)}` : "--"}
              </span>
            </div>
          );
        })}
      </div>

      {/* Brake bias */}
      <div className="flex items-center justify-between text-xs mb-2">
        <span className="text-rc-muted font-mono uppercase">Bias</span>
        <span className="font-mono font-bold text-rc-accent">
          {brakeBias > 0 ? `${brakeBias.toFixed(1)}%` : "--"}
        </span>
      </div>
      {/* Bias bar */}
      <div className="h-2 bg-rc-bg rounded-full overflow-hidden flex mb-3">
        <div
          className="h-full bg-cyan-500 transition-all duration-300"
          style={{ width: `${Math.min(brakeBias, 100)}%` }}
        />
      </div>

      {/* Pad & disc summary */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-1">
        {WHEEL_LABELS.map((label, i) => {
          const pad = wheels?.[i]?.pad_life ?? 0;
          const disc = wheels?.[i]?.disc_life ?? 0;
          return (
            <div key={label} className="flex items-center justify-between text-[10px]">
              <span className="text-rc-muted">{label}</span>
              <span className="font-mono text-rc-text">
                P:{pad.toFixed(0)}% D:{disc.toFixed(0)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
