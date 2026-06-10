import { useEffect, useRef, useState } from "react";
import {
  capturePhoto,
  composeSession,
  createSession,
  getSession,
  sessionImageUrl,
  sessionQrUrl,
  type SessionMetadata,
} from "./api/client";
import { PhotoStripPreview } from "./components/PhotoStripPreview";
import { QrPanel } from "./components/QrPanel";

type BusyAction = "session" | "capture1" | "capture2" | "compose" | null;
type PageState =
  | { name: "start" }
  | { name: "capture" }
  | { name: "result"; sessionId: string };

function getPageFromLocation(): PageState {
  const match = window.location.pathname.match(/^\/result\/([^/]+)$/);
  if (match) {
    return { name: "result", sessionId: decodeURIComponent(match[1]) };
  }
  if (window.location.pathname === "/shoot") {
    return { name: "capture" };
  }
  return { name: "start" };
}

function pushPage(page: PageState) {
  const path =
    page.name === "result"
      ? `/result/${encodeURIComponent(page.sessionId)}`
      : page.name === "capture"
        ? "/shoot"
        : "/";
  window.history.pushState({}, "", path);
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Unknown error.";
}

function wait(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

export default function App() {
  const [page, setPage] = useState<PageState>(() => getPageFromLocation());
  const [session, setSession] = useState<SessionMetadata | null>(null);
  const [busyAction, setBusyAction] = useState<BusyAction>(null);
  const [countdownValue, setCountdownValue] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const autoCreatingSession = useRef(false);

  useEffect(() => {
    const onPopState = () => setPage(getPageFromLocation());
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    if (page.name !== "result") {
      return;
    }
    if (session?.session_id === page.sessionId) {
      return;
    }

    setError(null);
    getSession(page.sessionId)
      .then(setSession)
      .catch((error: unknown) => setError(`Result load failed: ${getErrorMessage(error)}`));
  }, [page, session?.session_id]);

  useEffect(() => {
    if (page.name !== "capture" || session || autoCreatingSession.current) {
      return;
    }

    autoCreatingSession.current = true;
    setBusyAction("session");
    setError(null);
    createSession()
      .then(setSession)
      .catch((error: unknown) => setError(getErrorMessage(error)))
      .finally(() => {
        autoCreatingSession.current = false;
        setBusyAction(null);
      });
  }, [page.name, session]);

  const busy = busyAction !== null;
  const busySlot = busyAction === "capture1" ? 1 : busyAction === "capture2" ? 2 : null;

  async function runCountdown() {
    for (const value of [7, 6, 5, 4, 3, 2, 1]) {
      setCountdownValue(value);
      await wait(1000);
    }
    setCountdownValue(null);
  }

  const goHome = () => {
    setSession(null);
    setError(null);
    pushPage({ name: "start" });
    setPage({ name: "start" });
  };

  async function captureSlot(slot: 1 | 2) {
    if (!session || busy) {
      return;
    }

    setError(null);
    setBusyAction(slot === 1 ? "capture1" : "capture2");
    try {
      await runCountdown();
      const capturedSession = await capturePhoto(session.session_id, slot);
      setSession(capturedSession);

      if (slot === 2) {
        setBusyAction("compose");
        const composedSession = await composeSession(capturedSession.session_id);
        setSession(composedSession);
        const resultPage = { name: "result", sessionId: composedSession.session_id } as const;
        pushPage(resultPage);
        setPage(resultPage);
      }
    } catch (error: unknown) {
      setError(getErrorMessage(error));
    } finally {
      setCountdownValue(null);
      setBusyAction(null);
    }
  }

  const resultSession = session?.session_id === (page.name === "result" ? page.sessionId : "")
    ? session
    : null;

  return (
    <main className={page.name === "capture" ? "capture-screen" : "app-shell"}>
      <section
        className={
          page.name === "capture"
            ? "capture-stage"
            : page.name === "start"
              ? "start-page"
              : "capture-workspace"
        }
      >
        {error && (
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}

        {page.name === "start" && (
          <div className="start-panel">
            <p className="eyebrow">Reshot</p>
            <h1>Ready to shoot</h1>
            <button
              className="primary-action start-button"
              onClick={() => {
                setSession(null);
                setError(null);
                pushPage({ name: "capture" });
                setPage({ name: "capture" });
              }}
              type="button"
            >
              Start
            </button>
          </div>
        )}

        {page.name === "capture" && (
          <>
            <PhotoStripPreview
              session={session}
              busySlot={busySlot}
              countdownValue={countdownValue}
              onCapture={captureSlot}
            />
            {(busyAction === "session" || busyAction === "compose") && (
              <div className="capture-overlay" aria-live="polite">
                {busyAction === "compose" ? "Composing" : "Preparing"}
              </div>
            )}
          </>
        )}

        {page.name === "result" && resultSession && (
          <>
            <QrPanel
              sessionId={resultSession.session_id}
              imageUrl={`${sessionImageUrl(resultSession.session_id)}?t=${resultSession.updated_at}`}
              onGoHome={goHome}
              qrUrl={`${sessionQrUrl(resultSession.session_id)}?t=${resultSession.updated_at}`}
            />
            <div className="result-actions">
              <button type="button" onClick={goHome}>
                Go to start
              </button>
            </div>
          </>
        )}

        {page.name === "result" && !resultSession && !error && (
          <div className="empty-state">Loading result...</div>
        )}
      </section>
    </main>
  );
}
