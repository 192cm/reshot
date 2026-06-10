type QrPanelProps = {
  imageUrl: string;
  onGoHome: () => void;
  qrUrl: string;
  sessionId: string;
};

export function QrPanel({ imageUrl, onGoHome, qrUrl, sessionId }: QrPanelProps) {
  return (
    <section className="result-panel" aria-label="Shooting result">
      <div className="final-image-wrap">
        <img src={imageUrl} alt="Final composed result" />
      </div>
      <aside className="qr-card">
        <p className="eyebrow">Session {sessionId}</p>
        <h2>Scan QR</h2>
        <img className="qr-image" src={qrUrl} alt="Result image QR code" />
        <p>Scan from a phone on the same hotspot or LAN.</p>
        <button type="button" onClick={onGoHome}>
          Go to start
        </button>
      </aside>
    </section>
  );
}
