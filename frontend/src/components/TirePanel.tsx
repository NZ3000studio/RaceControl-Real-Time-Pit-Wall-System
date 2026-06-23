import { useTelemetryStore } from "../store/telemetryStore";
import type { WheelData } from "../types/telemetry";

const WHEEL_LABELS = ["FL", "FR", "RL", "RR"] as const;

function tempColor(value: number | null): string {
  if (value === null) return "text-rc-muted";
  if (value > 110) return "text-rc-danger";
  if (value > 100) return "text-rc-warn";
  if (value >= 80) return "text-rc-good";
  return "text-rc-accent";
}

function wearColor(value: number | null): string {
  if (value === null) return "bg-rc-border";
  if (value > 70) return "bg-rc-good";
  if (value >= 40) return "bg-rc-warn";
  return "bg-rc-danger";
}

function lifeColor(value: number | null): string {
  if (value === null) return "bg-rc-border";
  if (value > 60) return "bg-rc-good";
  if (value >= 30) return "bg-rc-warn";
  return "bg-rc-danger";
}

function fmt(value: number | null, decimals = 0): string {
  if (value === null) return "--";
  return value.toFixed(decimals);
}

function TempLayer({
  label,
  value,
}: {
  label: string;
  value: number | null;
}) {
  return (
    <div className="flex items-center justify-between text-[10px]">
      <span className="text-rc-muted">{label}</span>
      <span className={`font-mono ${tempColor(value)}`}>
        {fmt(value, 1)}&deg;
      </span>
    </div>
  );
}

function TireCell({ label, wheel }: { label: string; wheel: WheelData | null }) {
  const surfaceTemp = wheel?.temperature ?? null;
  const wear = wheel?.wear ?? null;
  const brakeTemp = wheel?.brake_temperature ?? null;
  const pressure = wheel?.pressure ?? null;
  const coreTemp = wheel?.tire_core_temp ?? null;
  const innerTemp = wheel?.temp_inner ?? null;
  const middleTemp = wheel?.temp_middle ?? null;
  const outerTemp = wheel?.temp_outer ?? null;
  const padLife = wheel?.pad_life ?? null;
  const discLife = wheel?.disc_life ?? null;

  return (
    <div className="flex flex-col gap-1.5 rounded border border-rc-border bg-rc-surface p-2.5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-bold text-rc-text">{label}</span>
        <span
          className={`h-2 w-2 rounded-full ${
            tempColor(surfaceTemp).replace("text-", "bg-")
          }`}
        />
      </div>

      {/* Tire layers: surface, core, inner, middle, outer */}
      <div className="bg-rc-bg rounded p-1.5 flex flex-col gap-0.5">
        <TempLayer label="Surf" value={surfaceTemp} />
        <TempLayer label="Core" value={coreTemp} />
        <TempLayer label="In" value={innerTemp} />
        <TempLayer label="Mid" value={middleTemp} />
        <TempLayer label="Out" value={outerTemp} />
      </div>

      {/* Pressure */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-rc-muted">Press</span>
        <span className="font-mono text-rc-text">{fmt(pressure, 1)} psi</span>
      </div>

      {/* Wear bar */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-rc-muted">Wear</span>
        <span className="font-mono text-rc-text">{fmt(wear, 0)}%</span>
      </div>
      <div className="h-1 overflow-hidden rounded-full bg-rc-border">
        <div
          className={`h-full rounded-full transition-all duration-300 ${wearColor(wear)}`}
          style={{
            width: `${wear !== null ? Math.min(Math.max(wear, 0), 100) : 0}%`,
          }}
        />
      </div>

      {/* Brake temp */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-rc-muted">Brk tmp</span>
        <span className={`font-mono ${tempColor(brakeTemp)}`}>
          {fmt(brakeTemp, 0)}&deg;C
        </span>
      </div>

      {/* Pad / disc life */}
      <div className="flex gap-2 text-[10px]">
        <div className="flex-1 flex flex-col gap-0.5">
          <span className="text-rc-muted">Pad</span>
          <div className="h-1 overflow-hidden rounded-full bg-rc-border">
            <div
              className={`h-full rounded-full ${lifeColor(padLife)}`}
              style={{ width: `${padLife ?? 0}%` }}
            />
          </div>
        </div>
        <div className="flex-1 flex flex-col gap-0.5">
          <span className="text-rc-muted">Disc</span>
          <div className="h-1 overflow-hidden rounded-full bg-rc-border">
            <div
              className={`h-full rounded-full ${lifeColor(discLife)}`}
              style={{ width: `${discLife ?? 0}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TirePanel() {
  const data = useTelemetryStore((s) => s.data);
  const wheels = data?.physics?.wheels ?? [null, null, null, null];

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4">
      <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold mb-3">
        Tires & Brakes
      </h2>
      <div className="grid grid-cols-2 gap-2">
        {WHEEL_LABELS.map((label, i) => (
          <TireCell key={label} label={label} wheel={wheels[i] ?? null} />
        ))}
      </div>
    </div>
  );
}
