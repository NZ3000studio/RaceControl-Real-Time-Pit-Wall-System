import { useEffect } from "react";
import { createTelemetrySocket } from "../services/websocket";
import { useTelemetryStore } from "../store/telemetryStore";

export function useTelemetrySocket(): void {
  const setData = useTelemetryStore((s) => s.setData);
  const setConnected = useTelemetryStore((s) => s.setConnected);

  useEffect(() => {
    const cleanup = createTelemetrySocket(setData, setConnected);
    return cleanup;
  }, [setData, setConnected]);
}
