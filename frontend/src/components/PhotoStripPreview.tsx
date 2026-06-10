import {
  oldPhotoUrl,
  sessionCaptureUrl,
  type SessionMetadata,
} from "../api/client";

type PhotoStripPreviewProps = {
  session: SessionMetadata | null;
  busySlot: 1 | 2 | null;
  countdownValue: number | null;
  onCapture: (slot: 1 | 2) => void;
};

type Slot = {
  key: "old_1" | "current_1" | "old_2" | "current_2";
  label: string;
  className: string;
};

const slots: Slot[] = [
  { key: "old_1", label: "Old 1", className: "slot-old-1" },
  { key: "current_1", label: "Current 1", className: "slot-current-1" },
  { key: "old_2", label: "Old 2", className: "slot-old-2" },
  { key: "current_2", label: "Current 2", className: "slot-current-2" },
];

function hasCapture(session: SessionMetadata | null, slot: 1 | 2): boolean {
  if (!session) {
    return false;
  }
  if (["ready_to_compose", "composed"].includes(session.status)) {
    return true;
  }
  return session.status === `captured_${slot}`;
}

function getSlotImage(session: SessionMetadata | null, key: Slot["key"]): string | null {
  const updatedAt = session?.updated_at ?? "initial";
  if (key === "old_1") {
    return `${oldPhotoUrl(1)}?t=${updatedAt}`;
  }
  if (key === "old_2") {
    return `${oldPhotoUrl(2)}?t=${updatedAt}`;
  }
  if (key === "current_1" && session && hasCapture(session, 1)) {
    return `${sessionCaptureUrl(session.session_id, 1)}?t=${session.updated_at}`;
  }
  if (key === "current_2" && session && hasCapture(session, 2)) {
    return `${sessionCaptureUrl(session.session_id, 2)}?t=${session.updated_at}`;
  }
  return null;
}

function getSlotForCurrent(currentSlot: 1 | 2): Slot {
  return slots.find((slot) => slot.key === `current_${currentSlot}`) ?? slots[1];
}

export function PhotoStripPreview({
  session,
  busySlot,
  countdownValue,
  onCapture,
}: PhotoStripPreviewProps) {
  const enlargedSlot = busySlot ? getSlotForCurrent(busySlot) : null;
  const enlargedImageUrl = enlargedSlot ? getSlotImage(session, enlargedSlot.key) : null;

  return (
    <section className="print-preview" aria-label="Final print frame preview">
      <div className="print-sheet">
        <div className="print-logo-space" aria-hidden="true" />
        {slots.map((slot) => {
          const imageUrl = getSlotImage(session, slot.key);
          const currentSlot =
            slot.key === "current_1" ? 1 : slot.key === "current_2" ? 2 : null;
          const isClickable =
            currentSlot !== null &&
            session !== null &&
            busySlot === null &&
            (currentSlot === 1 || hasCapture(session, 1));
          const content = imageUrl ? (
            <img src={imageUrl} alt={slot.label} />
          ) : (
            <span>{busySlot === currentSlot ? "Capturing..." : `Tap ${slot.label}`}</span>
          );

          if (currentSlot) {
            return (
              <button
                className={`print-slot print-slot-button ${slot.className}`}
                disabled={!isClickable}
                key={slot.key}
                onClick={() => onCapture(currentSlot)}
                type="button"
              >
                {content}
              </button>
            );
          }

          return (
            <div className={`print-slot ${slot.className}`} key={slot.key}>
              {content}
            </div>
          );
        })}
      </div>
      {enlargedSlot && (
        <div className="slot-preview-overlay" aria-live="polite">
          <div className="slot-preview-card">
            {enlargedImageUrl ? (
              <img src={enlargedImageUrl} alt={`${enlargedSlot.label} preview`} />
            ) : (
              <span>{enlargedSlot.label}</span>
            )}
            <strong>{countdownValue ?? "Capturing"}</strong>
          </div>
        </div>
      )}
    </section>
  );
}
