/** Telemetry types matching backend NormalizedTelemetry Pydantic model. */

export interface WheelData {
  temperature: number;
  wear: number;
  load: number;
  slip: number;
  brake_temperature: number;
  pressure: number;
  tire_core_temp: number;
  temp_inner: number;
  temp_middle: number;
  temp_outer: number;
  brake_pressure: number;
  pad_life: number;
  disc_life: number;
  tyre_force_x: number;
  tyre_force_y: number;
  self_aligning_torque: number;
}

export interface EngineData {
  rpm: number;
  max_rpm: number;
  throttle: number;
  brake: number;
  clutch: number;
  kers_charge: number;
  kers_current_kj: number;
  ers_power_level: number;
  ers_recovery_level: number;
  ers_is_charging: boolean;
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
  heading: number;
  pitch: number;
  roll: number;
  car_damage: number[];
  suspension_damage: number[];
  brake_bias: number;
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
  track_grip_level: number;
  drs_available: boolean;
  drs_engaged: boolean;
  tc_in_action: boolean;
  abs_in_action: boolean;
  rain_lights: boolean;
  rain_tires: boolean;
  wind_speed: number;
  wind_direction: number;
  flag: number;
  pit_limiter: boolean;
  tyre_compound: string;
  delta_lap_time: number;
  is_delta_positive: boolean;
  fuel_used_per_lap: number;
  penalty_time: number;
  penalty: number;
  stint_time_left: number;
  number_of_laps: number;
  tc_cut: number;
  clock: number;
  mandatory_pit_done: boolean;
}

export interface StaticData {
  car_model: string;
  track_name: string;
  player_name: string;
  air_temp: number;
  road_temp: number;
  pit_window_start: number;
  pit_window_end: number;
  max_power: number;
  max_torque: number;
  kers_max_j: number;
  ers_max_j: number;
  is_timed_race: boolean;
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

/** Track flag labels */
export const FLAG_LABELS: Record<number, string> = {
  0: "Green",
  1: "Yellow",
  2: "Blue",
  3: "White",
  4: "Checkered",
};

/** Damage zone labels */
export const DAMAGE_ZONE_LABELS = [
  "Body",
  "Engine",
  "Aero",
  "Susp F",
  "Susp R",
] as const;
