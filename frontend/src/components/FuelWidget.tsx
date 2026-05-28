import { useTelemetryStore } from "../store/telemetryStore";

function getFuelColor(percentage: number | null): string {
  if (percentage === null) return "bg-rc-muted";
  if (percentage > 30) return "bg-rc-good";
  if (percentage >= 10) return "bg-rc-warn";
  return "bg-rc-danger";
}

function getFuelTextColor(percentage: number | null): string {
  if (percentage === null) return "text-rc-muted";
  if (percentage > 30) return "text-rc-good";
  if (percentage >= 10) return "text-rc-warn";
  return "text-rc-danger";
}

export default function FuelWidget() {
  const data = useTelemetryStore((s) => s.data);

  const physics = data?.physics;
  const graphics = data?.graphics;
  const fuelRemaining = physics?.fuel ?? null;
  const maxFuel = physics?.max_fuel ?? null;
  const lapsRemaining = graphics?.fuel_estimate_remaining_laps ?? null;

  const fuelPercent =
    fuelRemaining !== null && maxFuel !== null && maxFuel > 0
      ? (fuelRemaining / maxFuel) * 100
      : null;

  const fuelBarColor = getFuelColor(fuelPercent);
  const fuelLabelColor = getFuelTextColor(fuelPercent);

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4 flex flex-col gap-3">
      <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold">
        Fuel
      </h2>

      <div className="w-full h-3 bg-rc-border rounded overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${fuelBarColor}`}
          style={{
            width: fuelPercent !== null ? `${Math.min(fuelPercent, 100)}%` : "0%",
          }}
        />
      </div>

      <div className="flex justify-between items-baseline">
        <span className={`text-2xl font-mono font-bold ${fuelLabelColor}`}>
          {fuelRemaining !== null ? `${fuelRemaining.toFixed(1)} L` : "---"}
        </span>
        <span className="text-rc-muted font-mono text-sm">
          / {maxFuel !== null ? `${maxFuel} L` : "---"}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-rc-muted text-xs uppercase tracking-wider">
          Laps Remaining
        </span>
        <span className="text-rc-text font-mono text-lg font-bold">
          {lapsRemaining !== null ? lapsRemaining : "---"}
        </span>
      </div>
    </div>
  );
}
