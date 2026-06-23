import { useTelemetryStore } from "../store/telemetryStore";
import { DAMAGE_ZONE_LABELS } from "../types/telemetry";

function damageColor(pct: number): string {
  if (pct < 5) return "bg-green-600";
  if (pct < 20) return "bg-yellow-500";
  if (pct < 50) return "bg-orange-500";
  return "bg-red-500";
}

export default function DamagePanel() {
  const data = useTelemetryStore((s) => s.data);
  const carDamage = data?.physics?.car_damage ?? [0, 0, 0, 0, 0];
  const suspDamage = data?.physics?.suspension_damage ?? [0, 0, 0, 0];

  const totalDamage = [...carDamage, ...suspDamage].reduce(
    (sum, v) => sum + v,
    0,
  );

  // If no damage at all, show clean state
  if (totalDamage === 0) {
    return (
      <div className="bg-rc-surface border border-rc-border rounded p-4">
        <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold mb-2">
          Damage
        </h2>
        <div className="flex items-center gap-2 text-xs">
          <span className="h-2 w-2 rounded-full bg-green-600" />
          <span className="text-rc-muted font-mono">No damage</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4">
      <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold mb-3">
        Damage
      </h2>

      <div className="flex flex-col gap-2">
        {/* 5 body zones */}
        {DAMAGE_ZONE_LABELS.map((label, i) => (
          <div key={label} className="flex items-center gap-2">
            <span className="text-[10px] text-rc-muted font-mono uppercase w-12">
              {label}
            </span>
            <div className="flex-1 h-2 bg-rc-bg rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${damageColor(carDamage[i] ?? 0)}`}
                style={{ width: `${Math.min(carDamage[i] ?? 0, 100)}%` }}
              />
            </div>
            <span className="text-[10px] font-mono text-rc-text w-8 text-right">
              {(carDamage[i] ?? 0).toFixed(0)}%
            </span>
          </div>
        ))}

        {/* Suspension damage summary */}
        {suspDamage.some((v) => v > 0) && (
          <div className="mt-1 pt-1 border-t border-rc-border">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-rc-muted font-mono uppercase w-12">
                Susp
              </span>
              <div className="flex-1 flex gap-1">
                {["FL", "FR", "RL", "RR"].map((label, i) => (
                  <div
                    key={label}
                    className="flex-1 text-center"
                    title={`${label}: ${suspDamage[i]?.toFixed(0)}%`}
                  >
                    <div className="h-3 bg-rc-bg rounded-sm overflow-hidden">
                      <div
                        className={`h-full ${damageColor(suspDamage[i] ?? 0)}`}
                        style={{
                          width: `${Math.min(suspDamage[i] ?? 0, 100)}%`,
                        }}
                      />
                    </div>
                    <span className="text-[9px] text-rc-muted">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
