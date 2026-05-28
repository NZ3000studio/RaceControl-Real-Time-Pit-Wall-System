/** Telemetry types matching backend NormalizedTelemetry Pydantic model. */

export interface WheelData {
  temperature: number;
  wear: number;
  load: number;
  slip: number;
  brake_temperature: number;
}

export interface EngineData {
  rpm: number;
  max_rpm: number;
  throttle: number;
  brake: number;
  clutch: number;
}

export interface PhysicsData {
  speed: number;
  velocity_x: number;
  velocity_y: number;
  velocity_z: number;
  acceleration_x: number;
  acceleration_y: number;
  acceleration_z: number;
  rpm: number;
  gear: number;
  throttle: number;
  brake: number;
  handbrake: number;
  steering: number;
  fuel: number;
  max_fuel: number;
  wheels: WheelData[];
  engine: EngineData;
  velocity: number;
  g_force: number;
}

export interface GraphicsData {
  session_type: number;
  session_status: number;
  completed_laps: number;
  current_lap: number;
  current_sector: number;
  last_sector_time: number;
  lap_time: number;
  position: number;
  num_cars: number;
  fuel_estimate_remaining_laps: number;
  abs: number;
  tc: number;
}

export interface StaticData {
  car_model: string;
  track_name: string;
  player_name: string;
  air_temp: number;
  road_temp: number;
}

export interface NormalizedTelemetry {
  physics: PhysicsData;
  graphics: GraphicsData;
  static: StaticData;
  timestamp: string;
}

/** Session type labels */
export const SESSION_TYPE_LABELS: Record<number, string> = {
  0: "Practice",
  1: "Qualifying",
  2: "Race",
  3: "Hotlap",
  4: "Time Attack",
  5: "Drift",
};

/** Session status labels */
export const SESSION_STATUS_LABELS: Record<number, string> = {
  0: "Off",
  1: "Replay",
  2: "Live",
  3: "Paused",
};
