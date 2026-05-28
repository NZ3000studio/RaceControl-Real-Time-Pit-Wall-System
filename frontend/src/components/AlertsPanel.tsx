import { useTelemetryStore } from "../store/telemetryStore";

const levelConfig = {
  info: { dot: "bg-rc-accent", label: "INFO" },
  warn: { dot: "bg-rc-warn", label: "WARN" },
  danger: { dot: "bg-rc-danger", label: "DANGER" },
} as const;

export default function AlertsPanel() {
  const alerts = useTelemetryStore((s) => s.alerts);
  const hasAlerts = alerts.length > 0;

  return (
    <div className="bg-rc-surface border border-rc-border rounded p-4 flex flex-col gap-2">
      <h2 className="text-rc-muted text-sm uppercase tracking-wider font-semibold">
        Alerts
      </h2>

      <div className={hasAlerts ? "max-h-48 overflow-y-auto space-y-1.5" : ""}>
        {!hasAlerts ? (
          <div className="flex items-center gap-2 text-sm">
            <span className="inline-block w-2 h-2 rounded-full bg-rc-good shrink-0" />
            <span className="text-rc-muted">All systems nominal</span>
          </div>
        ) : (
          alerts.map((alert) => {
            const cfg = levelConfig[alert.level] ?? levelConfig.info;
            return (
              <div key={alert.id} className="flex items-start gap-2 text-sm">
                <span className={`inline-block w-2 h-2 rounded-full mt-1.5 shrink-0 ${cfg.dot}`} />
                <span className="text-rc-text">{alert.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
