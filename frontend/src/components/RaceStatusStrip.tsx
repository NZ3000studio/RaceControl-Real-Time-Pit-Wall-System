import { useTelemetryStore } from "../store/telemetryStore";
import { FLAG_LABELS } from "../types/telemetry";

function StatusBadge({
  active,
  activeColor,
  inactiveColor,
  label,
}: {
  active: boolean;
  activeColor: string;
  inactiveColor: string;
  label: string;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <span
        className={`h-2 w-2 rounded-full ${
          active ? activeColor : inactiveColor
        }`}
      />
      <span
        className={`text-xs font-mono uppercase ${
          active ? "text-rc-text" : "text-rc-muted"
        }`}
      >
        {label}
      </span>
    </div>
  );
}

export default function RaceStatusStrip() {
  const data = useTelemetryStore((s) => s.data);
  const g = data?.graphics;

  if (!data) {
    return (
      <div className="bg-rc-surface border border-rc-border rounded px-4 py-2 flex items-center gap-6 opacity-50">
        <span className="text-xs text-rc-muted font-mono uppercase tracking-wider">
          Race Status -- Waiting for telemetry
        </span>
      </div>
    );
  }

  const drsAvail = g?.drs_available ?? false;
  const drsOn = g?.drs_engaged ?? false;
  const sector = g?.current_sector ?? 0;
  const flag = g?.flag ?? 0;
  const rainLights = g?.rain_lights ?? false;
  const rainTires = g?.rain_tires ?? false;
  const pitLimiter = g?.pit_limiter ?? false;
  const windSpeed = g?.wind_speed ?? 0;
  const windDir = g?.wind_direction ?? 0;
  const grip = g?.track_grip_level ?? 1;
  const tcActive = g?.tc_in_action ?? false;
  const absActive = g?.abs_in_action ?? false;

  return (
    <div className="bg-rc-surface border border-rc-border rounded px-4 py-2 flex flex-wrap items-center gap-x-6 gap-y-1">
      {/* DRS */}
      <StatusBadge
        active={drsOn}
        activeColor="bg-amber-400"
        inactiveColor={drsAvail ? "bg-green-600" : "bg-gray-600"}
        label={drsOn ? "DRS ON" : drsAvail ? "DRS RDY" : "DRS --"}
      />

      {/* Sector */}
      <div className="flex items-center gap-1.5">
        {[0, 1, 2].map((s) => (
          <span
            key={s}
            className={`text-xs font-mono px-1.5 py-0.5 rounded ${
              s === sector
                ? "bg-rc-accent text-white font-bold"
                : "bg-rc-bg text-rc-muted"
            }`}
          >
            S{s + 1}
          </span>
        ))}
      </div>

      {/* Flag */}
      <div className="flex items-center gap-1.5">
        <span
          className={`h-3 w-3 rounded-sm ${
            flag === 0
              ? "bg-green-500"
              : flag === 1
                ? "bg-yellow-400"
                : flag === 2
                  ? "bg-blue-500"
                  : flag === 4
                    ? "bg-white"
                    : "bg-gray-500"
          }`}
        />
        <span className="text-xs text-rc-text font-mono uppercase">
          {FLAG_LABELS[flag] ?? "?"}
        </span>
      </div>

      {/* Rain */}
      {(rainLights || rainTires) && (
        <StatusBadge
          active={true}
          activeColor="bg-blue-400"
          inactiveColor="bg-gray-600"
          label={rainTires ? "WET" : "RAIN"}
        />
      )}

      {/* Pit limiter */}
      {pitLimiter && (
        <StatusBadge
          active={true}
          activeColor="bg-red-500"
          inactiveColor="bg-gray-600"
          label="PIT"
        />
      )}

      {/* TC active */}
      {tcActive && (
        <StatusBadge
          active={true}
          activeColor="bg-orange-500"
          inactiveColor="bg-gray-600"
          label="TC"
        />
      )}

      {/* ABS active */}
      {absActive && (
        <StatusBadge
          active={true}
          activeColor="bg-orange-500"
          inactiveColor="bg-gray-600"
          label="ABS"
        />
      )}

      {/* Wind */}
      {windSpeed > 0 && (
        <div className="flex items-center gap-1">
          <span
            className="text-xs font-mono text-rc-muted inline-block"
            style={{ transform: `rotate(${windDir}deg)` }}
          >
            ↑
          </span>
          <span className="text-xs font-mono text-rc-text">
            {windSpeed.toFixed(1)} m/s
          </span>
        </div>
      )}

      {/* Grip */}
      <div className="flex items-center gap-1 ml-auto">
        <span className="text-xs text-rc-muted font-mono uppercase">Grip</span>
        <span className="text-xs font-mono text-rc-text font-bold">
          {(grip * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}
