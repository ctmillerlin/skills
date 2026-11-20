#!/usr/bin/env python3
"""Cross-platform headless screenshot & preview helper for tech-diagram."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import webbrowser


def find_browser() -> str | None:
    """Locate an installed Chromium-based browser on macOS, Windows, or Linux."""
    candidates: list[str] = []

    if sys.platform == "darwin":
        candidates.extend([
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ])
    elif sys.platform == "win32":
        rel_paths = [
            Path("Google/Chrome/Application/chrome.exe"),
            Path("Microsoft/Edge/Application/msedge.exe"),
            Path("Chromium/Application/chrome.exe"),
        ]
        for env_var in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(env_var)
            if base:
                candidates.extend(str(Path(base) / rel) for rel in rel_paths)
        candidates.extend(["chrome", "msedge", "chromium"])
    else:
        candidates.extend([
            "google-chrome",
            "google-chrome-stable",
            "chromium",
            "chromium-browser",
            "microsoft-edge",
        ])

    for candidate in candidates:
        path = Path(candidate)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def capture_view(
    browser: str,
    url: str,
    png_path: Path,
    profile_dir: Path,
    width: int,
    height: int,
) -> Path:
    """Render a single URL to a PNG screenshot using headless Chromium."""
    profile_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--virtual-time-budget=1500",
        f"--window-size={width},{height}",
        f"--user-data-dir={profile_dir}",
        f"--screenshot={png_path}",
    ]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        cmd.append("--no-sandbox")
    cmd.append(url)

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0 or not png_path.is_file():
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "no output"
        raise RuntimeError(f"Failed to capture {png_path.name}: {detail}")
    return png_path


def open_in_browser(uri: str) -> bool:
    """Open URI in a desktop browser when a graphical session is available."""
    if sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    ):
        return False
    return webbrowser.open(uri)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture light/dark (and multi-phase) screenshots of a tech-diagram HTML file."
    )
    parser.add_argument("html_file", help="Path to the self-contained HTML diagram file.")
    parser.add_argument(
        "--phases",
        type=int,
        default=0,
        help="Number of interactive states (captures phase=1..N light + phase=1 dark). Default: 0 (static light + dark).",
    )
    parser.add_argument("--width", type=int, default=1400, help="Viewport width in px (default: 1400).")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height in px (default: 1080).")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "tech-diagram-preview",
        help="Reusable output directory for preview PNGs (default: <tempdir>/tech-diagram-preview).",
    )
    parser.add_argument("--open", action="store_true", help="Open the HTML file in the desktop browser after capture.")
    parser.add_argument(
        "--open-only",
        action="store_true",
        help="Open the HTML file in the desktop browser without capturing screenshots.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    html_path = Path(args.html_file).expanduser().resolve()
    if not html_path.is_file():
        print(f"Error: HTML file not found: {html_path}", file=sys.stderr)
        return 1

    uri = html_path.as_uri()

    if args.open_only:
        if not open_in_browser(uri):
            print("Skipped opening browser (no graphical display detected).", file=sys.stderr)
        return 0

    if args.phases < 0:
        print("Error: --phases must be >= 0", file=sys.stderr)
        return 1

    browser = find_browser()
    if not browser:
        print(
            "Error: No Chromium-based browser (Chrome, Chromium, or Edge) found.",
            file=sys.stderr,
        )
        return 2

    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.phases == 0:
        views = [
            ("light", f"{uri}?theme=light"),
            ("dark", f"{uri}?theme=dark"),
        ]
    else:
        views = [(f"phase-{n}-light", f"{uri}?phase={n}&theme=light") for n in range(1, args.phases + 1)]
        views.append(("phase-1-dark", f"{uri}?phase=1&theme=dark"))

    errors: list[str] = []
    captured: list[Path] = []

    with ThreadPoolExecutor(max_workers=min(4, len(views))) as pool:
        futures = {
            pool.submit(
                capture_view,
                browser,
                url,
                out_dir / f"{name}.png",
                out_dir / f"profile-{name}",
                args.width,
                args.height,
            ): name
            for name, url in views
        }
        for future in as_completed(futures):
            try:
                captured.append(future.result())
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))

    for path in sorted(captured):
        print(path)

    if errors:
        for err in errors:
            print(f"Error: {err}", file=sys.stderr)
        return 1

    if args.open:
        open_in_browser(uri)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
