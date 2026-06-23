import { create } from "zustand";
import type { NormalizedTelemetry } from "../types/telemetry";

export interface Alert {
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

const WHEEL_LABELS = ["FL", "FR", "RL", "RR"] as const;

const computeAlerts = (data: NormalizedTelemetry): Alert[] => {
  const alerts: Alert[] = [];
  const { physics, graphics, static: staticData } = data;

  // ── Fuel ──────────────────────────────────────────────
  const fuelLaps = graphics.fuel_estimate_remaining_laps;
  if (fuelLaps <= 2 && fuelLaps > 0) {
    alerts.push({
      id: "fuel-critical",
      message: `CRITICAL: Fuel for ~${fuelLaps.toFixed(1)} laps`,
      level: "danger",
    });
  } else if (fuelLaps <= 5 && fuelLaps > 0) {
    alerts.push({
      id: "fuel-warn",
      message: `Fuel low — ~${fuelLaps.toFixed(1)} laps remaining`,
      level: "warn",
    });
  }

  // ── Tires ─────────────────────────────────────────────
  for (let i = 0; i < physics.wheels.length; i++) {
    const w = physics.wheels[i];
    const label = WHEEL_LABELS[i];

    // Heavy wear
    if (w.wear < 30) {
      alerts.push({
        id: `tire-wear-${i}`,
        message: `${label} tire heavily worn (${w.wear.toFixed(0)}%)`,
        level: "danger",
      });
    } else if (w.wear < 50) {
      alerts.push({
        id: `tire-wear-${i}`,
        message: `${label} tire wearing (${w.wear.toFixed(0)}%)`,
        level: "warn",
      });
    }

    // Overheating surface
    if (w.temperature > 110) {
      alerts.push({
        id: `tire-temp-${i}`,
        message: `${label} tire overheating — ${w.temperature.toFixed(0)}°C surface`,
        level: "warn",
      });
    }

    // Lockup / wheelspin
    if (w.slip > 0.5) {
      alerts.push({
        id: `slip-${i}`,
        message: `${label} lockup/wheelspin — slip ${(w.slip * 100).toFixed(0)}%`,
        level: "danger",
      });
    } else if (w.slip > 0.3) {
      alerts.push({
        id: `slip-${i}`,
        message: `${label} slipping — ${(w.slip * 100).toFixed(0)}%`,
        level: "warn",
      });
    }

    // Brake pad critical
    if (w.pad_life > 0 && w.pad_life < 15) {
      alerts.push({
        id: `pad-${i}`,
        message: `${label} brake pads critical (${w.pad_life.toFixed(0)}%)`,
        level: "danger",
      });
    }

    // Brake disc critical
    if (w.disc_life > 0 && w.disc_life < 15) {
      alerts.push({
        id: `disc-${i}`,
        message: `${label} brake disc critical (${w.disc_life.toFixed(0)}%)`,
        level: "danger",
      });
    }
  }

  // ── Engine ────────────────────────────────────────────
  if (physics.engine.rpm > physics.engine.max_rpm * 0.95) {
    alerts.push({
      id: "rpm-high",
      message: `Engine near redline — ${physics.engine.rpm.toFixed(0)} RPM`,
      level: "warn",
    });
  }

  // ── Damage ────────────────────────────────────────────
  const totalDamage = physics.car_damage?.reduce((s, v) => s + v, 0) ?? 0;
  const suspDamage = physics.suspension_damage?.reduce((s, v) => s + v, 0) ?? 0;

  if (totalDamage > 50 || suspDamage > 50) {
    alerts.push({
      id: "damage-severe",
      message: `Severe damage — repair needed`,
      level: "danger",
    });
  } else if (totalDamage > 20 || suspDamage > 20) {
    alerts.push({
      id: "damage-moderate",
      message: `Moderate damage — body: ${totalDamage.toFixed(0)}%`,
      level: "warn",
    });
  }

  // Engine damage specifically
  if ((physics.car_damage?.[1] ?? 0) > 20) {
    alerts.push({
      id: "engine-damage",
      message: `Engine damage — ${physics.car_damage[1].toFixed(0)}%`,
      level: "danger",
    });
  }

  // ── Track / Session ───────────────────────────────────
  if (graphics.drs_engaged) {
    alerts.push({ id: "drs", message: "DRS engaged", level: "info" });
  }

  if (graphics.tc_in_action) {
    alerts.push({ id: "tc", message: "TC active", level: "info" });
  }

  if (graphics.abs_in_action) {
    alerts.push({ id: "abs", message: "ABS active", level: "info" });
  }

  if (graphics.pit_limiter) {
    alerts.push({ id: "pit", message: "Pit limiter engaged", level: "info" });
  }

  if (graphics.rain_lights || graphics.rain_tires) {
    alerts.push({
      id: "rain",
      message: graphics.rain_tires ? "Rain tires equipped" : "Rain lights on",
      level: "warn",
    });
  }

  if (graphics.flag === 1) {
    alerts.push({
      id: "yellow-flag",
      message: "Yellow flag — caution",
      level: "warn",
    });
  }

  if (graphics.penalty_time > 0) {
    alerts.push({
      id: "penalty",
      message: `Penalty — ${graphics.penalty_time.toFixed(0)}s`,
      level: "danger",
    });
  }

  // Pit window
  if (
    staticData.pit_window_start > 0 &&
    graphics.current_lap >= staticData.pit_window_start &&
    graphics.current_lap <= staticData.pit_window_end
  ) {
    alerts.push({
      id: "pit-window",
      message: `Pit window open — lap ${staticData.pit_window_start}-${staticData.pit_window_end}`,
      level: "info",
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
