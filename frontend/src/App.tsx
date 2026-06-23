import { useTelemetrySocket } from "./hooks/useTelemetrySocket";
import { useTelemetryStore } from "./store/telemetryStore";
import SessionHeader from "./components/SessionHeader";
import RaceStatusStrip from "./components/RaceStatusStrip";
import TelemetryOverview from "./components/TelemetryOverview";
import SteeringGauge from "./components/SteeringGauge";
import GForceMeter from "./components/GForceMeter";
import FuelWidget from "./components/FuelWidget";
import ERSBattery from "./components/ERSBattery";
import TirePanel from "./components/TirePanel";
import BrakePanel from "./components/BrakePanel";
import DamagePanel from "./components/DamagePanel";
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

        {/* Race status strip — full width */}
        <RaceStatusStrip />

        {/* Main grid: 3 columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left column: primary telemetry + G-force */}
          <div className="space-y-4">
            <TelemetryOverview />
            <GForceMeter />
          </div>

          {/* Center column: steering + pace + alerts */}
          <div className="space-y-4">
            <SteeringGauge />
            <PaceGraph />
            <AlertsPanel />
          </div>

          {/* Right column: fuel + ERS + brakes + damage */}
          <div className="space-y-4">
            <FuelWidget />
            <ERSBattery />
            <BrakePanel />
            <DamagePanel />
          </div>
        </div>

        {/* Tire panel — full width for detailed per-tire data */}
        <TirePanel />
      </div>
    </div>
  );
}

export default App;
