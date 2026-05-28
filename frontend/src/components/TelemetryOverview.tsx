import { useTelemetryStore } from "../store/telemetryStore";

function speedColor(speed: number): string {
  if (speed < 80) return "text-green-400";
  if (speed < 180) return "text-yellow-400";
  return "text-red-400";
}

function rpmBarColor(pct: number): string {
  if (pct < 0.7) return "bg-green-500";
  if (pct < 0.9) return "bg-yellow-500";
  return "bg-red-500";
}

function formatGear(val: number | undefined): string {
  if (val === undefined || val === null) return "--";
  if (val === 0) return "R";
  if (val === 1) return "N";
  return String(Math.round(val));
}

function GaugeBar({ value, colorClass }: { value: number; colorClass: string }) {
  const pct = Math.min(Math.max(value, 0), 100);
  return (
    <div className="w-full h-3 bg-rc-surface rounded overflow-hidden border border-rc-border">
      <div
        className={`h-full transition-all duration-100 ease-linear ${colorClass}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export default function TelemetryOverview() {
  const data = useTelemetryStore((s) => s.data);

  const physics = data?.physics;
  const speedMs = physics?.speed ?? 0;
  const speedKmh = speedMs * 3.6;
  const rpm = physics?.rpm ?? 0;
  const maxRpm = physics?.engine?.max_rpm ?? 9000;
  const rpmPct = maxRpm > 0 ? rpm / maxRpm : 0;
  const gear = physics?.gear;
  const throttle = (physics?.throttle ?? 0) * 100;
  const brake = (physics?.brake ?? 0) * 100;

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4 flex flex-col gap-3">
      <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold">
        Telemetry
      </h2>

      <div className="grid grid-cols-2 gap-3">
        {/* Speed */}
        <div className="col-span-2 flex flex-col items-center">
          <span className={`text-6xl font-mono font-bold leading-none ${speedColor(speedKmh)}`}>
            {data ? `${Math.round(speedKmh)}` : "--"}
          </span>
          <span className="text-xs text-rc-muted font-mono mt-1">km/h</span>
        </div>

        {/* RPM */}
        <div className="col-span-2 flex flex-col gap-1">
          <div className="flex items-baseline justify-between">
            <span className="text-xs uppercase tracking-widest text-rc-muted font-mono">RPM</span>
            <span className="text-lg font-mono font-bold text-rc-text">
              {data ? Math.round(rpm) : "--"}
            </span>
          </div>
          <GaugeBar value={rpmPct * 100} colorClass={rpmBarColor(rpmPct)} />
        </div>

        {/* Gear */}
        <div className="flex flex-col items-center justify-center">
          <span className="text-xs uppercase tracking-widest text-rc-muted font-mono">Gear</span>
          <span className="text-5xl font-mono font-bold text-rc-accent mt-1">
            {formatGear(gear)}
          </span>
        </div>

        {/* Throttle & Brake */}
        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-0.5">
            <div className="flex justify-between">
              <span className="text-xs uppercase text-rc-muted font-mono">Thr</span>
              <span className="text-xs font-mono text-rc-text">{Math.round(throttle)}%</span>
            </div>
            <GaugeBar value={throttle} colorClass="bg-green-500" />
          </div>
          <div className="flex flex-col gap-0.5">
            <div className="flex justify-between">
              <span className="text-xs uppercase text-rc-muted font-mono">Brk</span>
              <span className="text-xs font-mono text-rc-text">{Math.round(brake)}%</span>
            </div>
            <GaugeBar value={brake} colorClass="bg-red-500" />
          </div>
        </div>
      </div>
    </div>
  );
}
