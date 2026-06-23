import { useTelemetryStore } from "../store/telemetryStore";
import {
  SESSION_TYPE_LABELS,
  SESSION_STATUS_LABELS,
} from "../types/telemetry";

const statusDotColor = (status: number): string => {
  switch (status) {
    case 2:
      return "bg-rc-good";
    case 3:
      return "bg-rc-warn";
    default:
      return "bg-gray-500";
  }
};

function formatStint(seconds: number): string {
  if (seconds <= 0) return "--";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function SessionHeader() {
  const data = useTelemetryStore((s) => s.data);
  const connected = useTelemetryStore((s) => s.connected);

  const sessionType =
    data != null
      ? SESSION_TYPE_LABELS[data.graphics.session_type] ?? "--"
      : "--";
  const sessionStatus =
    data != null
      ? SESSION_STATUS_LABELS[data.graphics.session_status] ?? "--"
      : "--";
  const statusNum = data?.graphics.session_status;

  const trackName = data?.static.track_name ?? "--";
  const carModel = data?.static.car_model ?? "--";
  const driverName = data?.static.player_name ?? "--";
  const currentLap = data?.graphics.current_lap ?? "--";
  const position = data?.graphics.position ?? "--";
  const numCars = data?.graphics.num_cars ?? "--";
  const airTemp = data?.static.air_temp ?? null;
  const roadTemp = data?.static.road_temp ?? null;
  const stintLeft = data?.graphics.stint_time_left ?? 0;
  const penaltyTime = data?.graphics.penalty_time ?? 0;
  const pitWindowStart = data?.static.pit_window_start ?? 0;
  const pitWindowEnd = data?.static.pit_window_end ?? 0;

  return (
    <header className="bg-rc-surface border-b border-rc-border px-4 py-2">
      <div className="flex items-center gap-3 text-sm flex-wrap">
        {/* Session type chip */}
        <span className="text-rc-accent font-semibold tracking-wide uppercase text-xs">
          {sessionType}
        </span>

        <span className="text-rc-border">|</span>

        {/* Status with colored dot */}
        <span className="flex items-center gap-1.5 text-rc-muted">
          {statusNum != null ? (
            <span
              className={`inline-block h-2 w-2 rounded-full ${statusDotColor(statusNum)}`}
            />
          ) : (
            <span className="inline-block h-2 w-2 rounded-full bg-gray-600" />
          )}
          <span>{sessionStatus}</span>
        </span>

        <span className="text-rc-border">|</span>

        {/* Track name */}
        <span className="text-rc-text">{trackName}</span>

        <span className="text-rc-border">|</span>

        {/* Car model */}
        <span className="text-rc-text">{carModel}</span>

        <span className="text-rc-border">|</span>

        {/* Driver name */}
        <span className="text-rc-text">{driverName}</span>

        <span className="text-rc-border">|</span>

        {/* Lap number */}
        <span className="text-rc-muted">
          Lap{" "}
          <span className="font-mono text-rc-text">{currentLap}</span>
        </span>

        <span className="text-rc-border">|</span>

        {/* Position */}
        <span className="text-rc-muted">
          Pos{" "}
          <span className="font-mono text-rc-text">
            {position}{numCars !== "--" ? `/${numCars}` : ""}
          </span>
        </span>

        {/* Right-aligned info group */}
        <span className="ml-auto flex items-center gap-3">
          {/* Temps */}
          <span className="text-xs text-rc-muted font-mono">
            Air{" "}
            <span className="text-rc-text">
              {airTemp !== null ? `${airTemp.toFixed(1)}°` : "--"}
            </span>
          </span>
          <span className="text-xs text-rc-muted font-mono">
            Track{" "}
            <span className="text-rc-text">
              {roadTemp !== null ? `${roadTemp.toFixed(1)}°` : "--"}
            </span>
          </span>

          {/* Pit window */}
          {pitWindowStart > 0 && (
            <>
              <span className="text-rc-border">|</span>
              <span className="text-xs text-rc-muted font-mono">
                Pit{" "}
                <span className="text-rc-text">
                  {pitWindowStart}-{pitWindowEnd}
                </span>
              </span>
            </>
          )}

          {/* Stint time left */}
          {stintLeft > 0 && (
            <>
              <span className="text-rc-border">|</span>
              <span className="text-xs text-rc-muted font-mono">
                Stint{" "}
                <span className="text-rc-text">
                  {formatStint(stintLeft)}
                </span>
              </span>
            </>
          )}

          {/* Penalty */}
          {penaltyTime > 0 && (
            <>
              <span className="text-rc-border">|</span>
              <span className="text-xs text-red-400 font-mono font-bold">
                PEN {penaltyTime.toFixed(0)}s
              </span>
            </>
          )}
        </span>

        {/* Disconnected indicator */}
        {!connected && (
          <span className="text-xs font-medium text-rc-warn">
            Disconnected
          </span>
        )}
      </div>
    </header>
  );
}
