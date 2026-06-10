type CountdownProps = {
  activeLabel: string;
  busy: boolean;
  value: number | null;
};

export function Countdown({ activeLabel, busy, value }: CountdownProps) {
  return (
    <div className="countdown" aria-live="polite">
      <span className="countdown-label">{busy ? "진행 중" : "대기 중"}</span>
      <strong>{value ?? activeLabel}</strong>
    </div>
  );
}
