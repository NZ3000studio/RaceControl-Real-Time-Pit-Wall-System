import { useTelemetryStore } from "../store/telemetryStore";

export default function ERSBattery() {
  const data = useTelemetryStore((s) => s.data);
  const engine = data?.physics?.engine;
  const kersKj = engine?.kers_current_kj ?? 0;
  const kersCharge = engine?.kers_charge ?? 0;
  const ersPower = engine?.ers_power_level ?? 0;
  const ersRecovery = engine?.ers_recovery_level ?? 0;
  const ersCharging = engine?.ers_is_charging ?? false;

  // Has ERS/KERS data?
  const hasKers = kersKj > 0 || kersCharge > 0;
  if (!hasKers) {
    return null; // Car doesn't have ERS/KERS, hide this panel
  }

  const chargePct = Math.min(kersCharge * 100, 100);

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold">
          ERS
        </h2>
        <span className="text-lg font-mono font-bold text-cyan-400">
          {kersKj.toFixed(0)} kJ
        </span>
      </div>

      {/* Battery gauge */}
      <div className="h-4 bg-rc-bg rounded-full overflow-hidden mb-2">
        <div
          className={`h-full transition-all duration-200 rounded-full ${
            chargePct > 60
              ? "bg-cyan-500"
              : chargePct > 30
                ? "bg-yellow-500"
                : "bg-red-500"
          }`}
          style={{ width: `${chargePct}%` }}
        />
      </div>

      {/* Deployment / Recovery info */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-rc-muted font-mono">Deploy</span>
          <span className="font-mono text-rc-text">{ersPower}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-rc-muted font-mono">Recover</span>
          <span className="font-mono text-rc-text">{ersRecovery}</span>
        </div>
        <div className="col-span-2 flex items-center gap-1.5">
          <span
            className={`h-2 w-2 rounded-full ${
              ersCharging ? "bg-green-500" : "bg-gray-600"
            }`}
          />
          <span className="font-mono text-rc-text">
            {ersCharging ? "Charging" : "Idle"}
          </span>
        </div>
      </div>
    </div>
  );
}
