import { create } from "zustand";
import type { NormalizedTelemetry } from "../types/telemetry";

interface Alert {
  id: string;
  message: string;
  level: "info" | "warn" | "danger";
}

interface TelemetryState {
  data: NormalizedTelemetry | null;
  connected: boolean;
  alerts: Alert[];

  setData: (data: NormalizedTelemetry) => void;
  setConnected: (connected: boolean) => void;
}

const computeAlerts = (data: NormalizedTelemetry): Alert[] => {
  const alerts: Alert[] = [];
  const { physics, graphics } = data;

  // Fuel warning
  if (graphics.fuel_estimate_remaining_laps <= 2) {
    alerts.push({
      id: "fuel-low",
      message: `Low fuel — ~${graphics.fuel_estimate_remaining_laps.toFixed(1)} laps remaining`,
      level: "danger",
    });
  } else if (graphics.fuel_estimate_remaining_laps <= 5) {
    alerts.push({
      id: "fuel-warn",
      message: `Fuel running low — ~${graphics.fuel_estimate_remaining_laps.toFixed(1)} laps remaining`,
      level: "warn",
    });
  }

  // Tire wear
  for (let i = 0; i < physics.wheels.length; i++) {
    const w = physics.wheels[i];
    const label = ["FL", "FR", "RL", "RR"][i];
    if (w.wear < 30) {
      alerts.push({
        id: `tire-wear-${i}`,
        message: `${label} tire heavily worn (${w.wear.toFixed(0)}%)`,
        level: "danger",
      });
    }
  }

  // Tire temp warning
  for (let i = 0; i < physics.wheels.length; i++) {
    const w = physics.wheels[i];
    const label = ["FL", "FR", "RL", "RR"][i];
    if (w.temperature > 110) {
      alerts.push({
        id: `tire-temp-${i}`,
        message: `${label} tire overheating (${w.temperature.toFixed(0)}C)`,
        level: "warn",
      });
    }
  }

  // Engine temp
  if (physics.engine.rpm > physics.engine.max_rpm * 0.95) {
    alerts.push({
      id: "rpm-high",
      message: `Engine near redline — ${physics.engine.rpm.toFixed(0)} RPM`,
      level: "warn",
    });
  }

  return alerts;
};

export const useTelemetryStore = create<TelemetryState>((set) => ({
  data: null,
  connected: false,
  alerts: [],

  setData: (data: NormalizedTelemetry) =>
    set({ data, alerts: computeAlerts(data) }),

  setConnected: (connected: boolean) =>
    set(connected ? { connected } : { connected, data: null }),
}));
