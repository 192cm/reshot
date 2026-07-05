import { useState } from "react";
import {
  sessionCaptureUrl,
  type CaptureSlot,
  type SessionMetadata,
} from "../api/client";
import { LiveCameraPreview } from "./LiveCameraPreview";

type PhotoStripPreviewProps = {
  session: SessionMetadata | null;
  busySlot: CaptureSlot | null;
  countdownValue: number | null;
  isComposing: boolean;
  onCapture: (slot: CaptureSlot) => void;
  onCompose: (slots: CaptureSlot[]) => void;
};

type FrameSlot = {
  label: string;
  className: string;
};

const captureSlots: CaptureSlot[] = [1, 2, 3, 4, 5, 6, 7, 8];

const frameSlots: FrameSlot[] = [
  { label: "Frame 1", className: "slot-old-1" },
  { label: "Frame 2", className: "slot-current-1" },
  { label: "Frame 3", className: "slot-current-2" },
  { label: "Frame 4", className: "slot-old-2" },
];

const frameLogoUrl = new URL("../../../assets/frames/mpnu-logo.png", import.meta.url).href;
const frameText = "매직PNU 홈커밍 26.07.04";

function capturedSlotNumbers(session: SessionMetadata | null): CaptureSlot[] {
  if (!session) {
    return [];
  }

  return session.captures
    .map((capture) => capture.match(/current_(\d+)\.jpg$/)?.[1])
    .map((slot) => Number(slot))
    .filter((slot): slot is CaptureSlot => captureSlots.includes(slot as CaptureSlot));
}

function captureUrl(session: SessionMetadata, slot: CaptureSlot): string {
  return `${sessionCaptureUrl(session.session_id, slot)}?t=${session.updated_at}`;
}

export function PhotoStripPreview({
  session,
  busySlot,
  countdownValue,
  isComposing,
  onCapture,
  onCompose,
}: PhotoStripPreviewProps) {
  const capturedSlots = capturedSlotNumbers(session);
  const nextSlot = captureSlots.find((slot) => !capturedSlots.includes(slot)) ?? null;
  const displayedCaptureCount = Math.min(captureSlots.length, busySlot ?? capturedSlots.length);
  const [activeFrameIndex, setActiveFrameIndex] = useState<number | null>(null);
  const [assignments, setAssignments] = useState<(CaptureSlot | null)[]>([null, null, null, null]);

  const allCaptured = capturedSlots.length >= captureSlots.length;
  const readyToCompose = assignments.every((slot) => slot !== null);
  function assignToFrame(frameIndex: number, captureSlot: CaptureSlot) {
    setAssignments((current) =>
      current.map((assignedSlot, index) => {
        if (index === frameIndex) {
          return captureSlot;
        }
        return assignedSlot === captureSlot ? null : assignedSlot;
      }),
    );
    setActiveFrameIndex(null);
  }

  if (!allCaptured) {
    const latestCapture =
      session && capturedSlots.length > 0
        ? (
            <img
              src={captureUrl(session, capturedSlots[capturedSlots.length - 1])}
              alt="Latest capture"
            />
          )
        : (
            <span>Ready</span>
          );

    return (
      <section className="shooting-flow" aria-label="Capture photos">
        <div className="shooting-main">
          <div className="shooting-camera-row">
            <LiveCameraPreview
              className="shooting-preview live-preview"
              controlsClassName="shooting-side-controls"
              fallback={latestCapture}
            >
              {busySlot && (
                <strong className="shooting-countdown">
                  {countdownValue ?? "촬영"}
                </strong>
              )}
            </LiveCameraPreview>
            <div className="shooting-progress" aria-label={`${displayedCaptureCount} of ${captureSlots.length} photos`} aria-live="polite">
              {displayedCaptureCount} / {captureSlots.length}
            </div>
            <button
              className="primary-action shutter-button"
              disabled={!session || busySlot !== null || nextSlot === null}
              onClick={() => nextSlot && onCapture(nextSlot)}
              type="button"
            >
              {busySlot ? `사진 촬영 중 ${busySlot} / 8` : "사진 촬영 시작하기"}
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="selection-flow" aria-label="Select final photos">
      <div className="selection-layout">
        <div className="print-preview selection-preview">
          <div className="print-sheet">
            <div className="print-logo-space" aria-hidden="true">
              <img src={frameLogoUrl} alt="" />
            </div>
            {frameSlots.map((frame, index) => {
              const assignedSlot = assignments[index];
              return (
                <button
                  className={`print-slot print-slot-button assign-slot ${frame.className}`}
                  key={frame.label}
                  onClick={() => setActiveFrameIndex(index)}
                  type="button"
                >
                  {session && assignedSlot ? (
                    <img src={captureUrl(session, assignedSlot)} alt={`${frame.label} capture ${assignedSlot}`} />
                  ) : (
                    <span>{frame.label}</span>
                  )}
                </button>
              );
            })}
            <div className="print-template-text" aria-hidden="true">
              {frameText}
            </div>
          </div>
          <button
            className="primary-action compose-button"
            disabled={!readyToCompose || isComposing}
            onClick={() => onCompose(assignments as CaptureSlot[])}
            type="button"
          >
            {isComposing ? "Composing..." : "Save final"}
          </button>
        </div>
      </div>
      {activeFrameIndex !== null && (
        <div className="capture-picker-overlay" role="dialog" aria-modal="true" aria-label={`${frameSlots[activeFrameIndex].label} photo choices`}>
          <div className="capture-picker-popover">
            {captureSlots.map((slot) => {
              const assigned = assignments.includes(slot);
              const selected = assignments[activeFrameIndex] === slot;
              return (
                <button
                  className={`capture-choice ${selected ? "is-selected" : ""} ${assigned ? "is-assigned" : ""}`}
                  key={slot}
                  onClick={() => assignToFrame(activeFrameIndex, slot)}
                  type="button"
                >
                  {session && <img src={captureUrl(session, slot)} alt={`Capture ${slot}`} />}
                  <span>{slot}</span>
                </button>
              );
            })}
            <button className="picker-close" onClick={() => setActiveFrameIndex(null)} type="button">
              Close
            </button>
          </div>
        </div>
      )}
    </section>
  );
}


