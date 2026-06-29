import { useState } from "react";

type QrPanelProps = {
  imageUrl: string;
  onGoHome: () => void;
  qrUrl: string;
  sessionId: string;
};

export function QrPanel({ imageUrl, onGoHome, qrUrl, sessionId }: QrPanelProps) {
  const [showQr, setShowQr] = useState(false);

  return (
    <section className="result-panel" aria-label="Shooting result">
      <div className="final-image-wrap">
        <img src={imageUrl} alt="Final composed result" />
      </div>
      <aside className="qr-card">
        <p className="eyebrow">Session {sessionId}</p>
        <button className="primary-action" type="button" onClick={() => setShowQr(true)}>
          QR 보기
        </button>
        <button type="button" onClick={onGoHome}>
          처음으로
        </button>
      </aside>
      {showQr && (
        <div className="qr-overlay" role="dialog" aria-modal="true" aria-label="Result QR code">
          <div className="qr-modal">
            <img className="qr-modal-image" src={qrUrl} alt="Result image QR code" />
            <button type="button" onClick={() => setShowQr(false)}>
              닫기
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
