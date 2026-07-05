const defaultApiBaseUrl = "http://localhost:8000";

export const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? defaultApiBaseUrl;

export type CaptureSlot = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

export type HealthResponse = {
  app: string;
  status: string;
  environment: string;
  camera_mode?: string;
};

export type SessionMetadata = {
  session_id: string;
  created_at: string;
  updated_at: string;
  status: string;
  template_id: string;
  final_image_path: string;
  qr_image_path: string | null;
  qr_target_url: string | null;
  drive_file_id: string | null;
  drive_share_url: string | null;
  old_photos: string[];
  captures: string[];
};

async function readJson<T>(response: Response): Promise<T> {
  if (response.ok) {
    return response.json() as Promise<T>;
  }

  let detail = `Request failed with ${response.status}`;
  try {
    const body = (await response.json()) as { detail?: string };
    if (body.detail) {
      detail = body.detail;
    }
  } catch {
    // Keep the status-based fallback.
  }

  throw new Error(detail);
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/health`);

  return readJson<HealthResponse>(response);
}

export async function createSession(): Promise<SessionMetadata> {
  const response = await fetch(`${apiBaseUrl}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ template_id: "default" }),
  });

  return readJson<SessionMetadata>(response);
}

export async function getSession(sessionId: string): Promise<SessionMetadata> {
  const response = await fetch(`${apiBaseUrl}/sessions/${sessionId}`);

  return readJson<SessionMetadata>(response);
}

export async function capturePhoto(
  sessionId: string,
  slot: CaptureSlot,
): Promise<SessionMetadata> {
  const response = await fetch(`${apiBaseUrl}/sessions/${sessionId}/capture`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ slot }),
  });

  return readJson<SessionMetadata>(response);
}

export async function composeSession(
  sessionId: string,
  selectedCaptureSlots: CaptureSlot[],
): Promise<SessionMetadata> {
  const response = await fetch(`${apiBaseUrl}/sessions/${sessionId}/compose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      template_id: "default",
      selected_capture_slots: selectedCaptureSlots,
    }),
  });

  return readJson<SessionMetadata>(response);
}

export function sessionImageUrl(sessionId: string): string {
  return `${apiBaseUrl}/sessions/${sessionId}/image`;
}

export function sessionQrUrl(sessionId: string): string {
  return `${apiBaseUrl}/sessions/${sessionId}/qr`;
}

export function sessionCaptureUrl(sessionId: string, slot: CaptureSlot): string {
  return `${apiBaseUrl}/sessions/${sessionId}/capture/${slot}`;
}
