import type { NormalizedTelemetry } from "../types/telemetry";

const WS_URL = "ws://localhost:8000/ws/telemetry";
const INITIAL_RECONNECT_MS = 500;
const MAX_RECONNECT_MS = 8000;

type TelemetryCallback = (data: NormalizedTelemetry) => void;
type StatusCallback = (connected: boolean) => void;

export function createTelemetrySocket(
  onTelemetry: TelemetryCallback,
  onStatus: StatusCallback,
): () => void {
  let ws: WebSocket | null = null;
  let reconnectDelay = INITIAL_RECONNECT_MS;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let stopped = false;

  function connect(): void {
    if (stopped) return;

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      reconnectDelay = INITIAL_RECONNECT_MS;
      onStatus(true);
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as NormalizedTelemetry;
        onTelemetry(data);
      } catch {
        // Skip malformed frames
      }
    };

    ws.onclose = () => {
      onStatus(false);
      ws = null;
      if (!stopped) scheduleReconnect();
    };

    ws.onerror = () => {
      ws?.close();
    };
  }

  function scheduleReconnect(): void {
    if (stopped) return;
    reconnectTimer = setTimeout(() => {
      reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_MS);
      connect();
    }, reconnectDelay);
  }

  connect();

  return () => {
    stopped = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    ws?.close();
  };
}
