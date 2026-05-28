import { useTelemetrySocket } from "./hooks/useTelemetrySocket";
import { useTelemetryStore } from "./store/telemetryStore";
import SessionHeader from "./components/SessionHeader";
import TelemetryOverview from "./components/TelemetryOverview";
import FuelWidget from "./components/FuelWidget";
import TirePanel from "./components/TirePanel";
import PaceGraph from "./components/PaceGraph";
import AlertsPanel from "./components/AlertsPanel";

function ConnectionBadge() {
  const connected = useTelemetryStore((s) => s.connected);

  return (
    <div className="fixed top-3 right-3 flex items-center gap-2 text-xs font-mono z-50">
      <span
        className={`h-2 w-2 rounded-full ${connected ? "bg-rc-good" : "bg-rc-danger"}`}
      />
      <span className="text-rc-muted">
        {connected ? "LIVE" : "DISCONNECTED"}
      </span>
    </div>
  );
}

function App() {
  useTelemetrySocket();

  return (
    <div className="min-h-screen bg-rc-bg p-4">
      <ConnectionBadge />

      <div className="max-w-[1600px] mx-auto space-y-4">
        {/* Session header — full width */}
        <SessionHeader />

        {/* Main grid: 3 columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left column: overview + alerts */}
          <div className="space-y-4">
            <TelemetryOverview />
            <AlertsPanel />
          </div>

          {/* Center column: pace graph (spans taller) */}
          <PaceGraph />

          {/* Right column: fuel + tires */}
          <div className="space-y-4">
            <FuelWidget />
            <TirePanel />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
