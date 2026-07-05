"""Create or refresh the Google Drive OAuth token for local uploads."""

from __future__ import annotations

from app.services.google_drive_service import run_interactive_authorization


def main() -> None:
    token_path = run_interactive_authorization()
    print(f"Saved Google Drive OAuth token: {token_path}")


if __name__ == "__main__":
    main()