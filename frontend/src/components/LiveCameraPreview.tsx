import { useEffect, useId, useRef, useState, type ReactNode } from "react";

type LiveCameraPreviewProps = {
  className?: string;
  controlsClassName?: string;
  fallback?: ReactNode;
  children?: ReactNode;
};

type PreviewStatus = "starting" | "live" | "unavailable";

function statusLabel(status: PreviewStatus): string {
  if (status === "live") {
    return "Live preview";
  }
  if (status === "starting") {
    return "Starting preview";
  }
  return "Preview unavailable";
}

const preferredDeviceStorageKey = "reshot.previewDeviceId";

function isCaptureCardLabel(label: string): boolean {
  return /capture|hdmi|cam link|usb video|uvc/i.test(label);
}

function preferredDeviceId(devices: MediaDeviceInfo[]): string {
  const savedDeviceId = window.localStorage.getItem(preferredDeviceStorageKey);
  if (savedDeviceId && devices.some((device) => device.deviceId === savedDeviceId)) {
    return savedDeviceId;
  }

  return devices.find((device) => isCaptureCardLabel(device.label))?.deviceId ?? devices[0]?.deviceId ?? "";
}

export function LiveCameraPreview({ children, className, controlsClassName, fallback }: LiveCameraPreviewProps) {
  const selectId = useId();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [status, setStatus] = useState<PreviewStatus>("starting");

  useEffect(() => {
    let cancelled = false;

    async function loadDevices() {
      if (!navigator.mediaDevices?.getUserMedia || !navigator.mediaDevices?.enumerateDevices) {
        setStatus("unavailable");
        return;
      }

      try {
        const permissionStream = await navigator.mediaDevices.getUserMedia({ audio: false, video: true });
        permissionStream.getTracks().forEach((track) => track.stop());

        const videoDevices = (await navigator.mediaDevices.enumerateDevices()).filter(
          (device) => device.kind === "videoinput",
        );

        if (cancelled) {
          return;
        }

        setDevices(videoDevices);
        setSelectedDeviceId(preferredDeviceId(videoDevices));
      } catch {
        setStatus("unavailable");
      }
    }

    loadDevices();

    const handleDeviceChange = () => loadDevices();
    navigator.mediaDevices?.addEventListener?.("devicechange", handleDeviceChange);

    return () => {
      cancelled = true;
      navigator.mediaDevices?.removeEventListener?.("devicechange", handleDeviceChange);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function startPreview() {
      if (!selectedDeviceId || !navigator.mediaDevices?.getUserMedia) {
        return;
      }

      setStatus("starting");
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {
            deviceId: { exact: selectedDeviceId },
            width: { ideal: 1920 },
            height: { ideal: 1080 },
          },
        });

        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }

        window.localStorage.setItem(preferredDeviceStorageKey, selectedDeviceId);
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setStatus("live");
      } catch {
        setStatus("unavailable");
      }
    }

    startPreview();

    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    };
  }, [selectedDeviceId]);

  return (
    <>
      <div className={className}>
        <video
          aria-label="Live camera preview"
          autoPlay
          muted
          playsInline
          ref={videoRef}
        />
        <span className={`live-preview-status live-preview-status-${status}`}>{statusLabel(status)}</span>
        {status !== "live" && (
          <div className="live-preview-fallback">
            <div className="live-preview-message"><strong>{statusLabel(status)}</strong>{fallback}</div>
          </div>
        )}
        {children}
      </div>
      <div className={controlsClassName}>
        <label className="live-preview-device" htmlFor={selectId}>
          <span>Preview source</span>
          <select
            aria-label="Preview source"
            disabled={devices.length === 0}
            id={selectId}
            onChange={(event) => setSelectedDeviceId(event.target.value)}
            value={selectedDeviceId}
          >
            {devices.length === 0 ? (
              <option value="">No camera source</option>
            ) : (
              devices.map((device, index) => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label || `Camera ${index + 1}`}
                </option>
              ))
            )}
          </select>
        </label>
      </div>
    </>
  );
}