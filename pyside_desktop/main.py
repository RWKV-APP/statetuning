#!/usr/bin/env python3
"""Entry point for the PySide desktop app.

Supported launches:
- python -m pyside_desktop.main   (from project root, while the folder keeps this name)
- python -m main                  (from this folder, even if the folder is renamed)
- python main.py                  (from this folder, even if the folder is renamed)
"""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import types
from pathlib import Path


_DYNAMIC_PACKAGE = "_statetuning_desktop_app"
_APP_VENV_DIR = Path(__file__).resolve().parent / ".venv"


def _is_virtualenv() -> bool:
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix) or hasattr(
        sys, "real_prefix"
    )


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _python_version(executable: str) -> tuple[int, int] | None:
    code = "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
    try:
        out = subprocess.check_output(
            [executable, "-c", code], stderr=subprocess.DEVNULL, text=True
        ).strip()
        major, minor = out.split(".", 1)
        return int(major), int(minor)
    except Exception:
        return None


def _select_venv_python() -> str:
    candidates: list[str] = []
    if sys.version_info < (3, 14):
        candidates.append(sys.executable)
    for name in ("python3.13", "python3.12", "python3.11", "python3.10", "python3"):
        path = shutil.which(name)
        if path and path not in candidates:
            candidates.append(path)

    for path in candidates:
        version = _python_version(path)
        if version and (3, 10) <= version < (3, 14):
            return path

    return sys.executable


def _ensure_app_venv_and_reexec() -> None:
    venv_python = _venv_python(_APP_VENV_DIR)
    if not venv_python.exists():
        python = _select_venv_python()
        print(f"PySide6 is not installed. Creating app venv: {_APP_VENV_DIR}")
        subprocess.check_call([python, "-m", "venv", str(_APP_VENV_DIR)])

    script = str(Path(__file__).resolve())
    os.execv(str(venv_python), [str(venv_python), script, *sys.argv[1:]])


def _install_pyside6() -> None:
    requirements = Path(__file__).with_name("requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])

    sources = []
    index_url = os.environ.get("PIP_INDEX_URL")
    if index_url:
        sources.append(index_url)
    sources.extend(
        [
            None,
            "https://pypi.tuna.tsinghua.edu.cn/simple",
            "https://mirrors.aliyun.com/pypi/simple",
        ]
    )

    seen: set[str | None] = set()
    last_error: subprocess.CalledProcessError | None = None
    print("PySide6 is not installed. Installing requirements into app venv...")

    for source in sources:
        if source in seen:
            continue
        seen.add(source)
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--progress-bar",
            "off",
            "--retries",
            "10",
            "--resume-retries",
            "10",
            "--timeout",
            "120",
        ]
        if source:
            cmd.extend(["-i", source])
        cmd.extend(["-r", str(requirements)])
        label = source or "default PyPI"
        print(f"  trying {label} ...")
        try:
            subprocess.check_call(cmd)
            return
        except subprocess.CalledProcessError as exc:
            last_error = exc
            print(f"  failed with {label}, retrying next source...")

    if last_error is not None:
        raise last_error


def _import_pyside6():
    try:
        from PySide6.QtCore import QLocale, Qt
        from PySide6.QtWidgets import QApplication
    except ModuleNotFoundError as exc:
        if exc.name != "PySide6":
            raise
        if not _is_virtualenv():
            _ensure_app_venv_and_reexec()
        _install_pyside6()
        from PySide6.QtCore import QLocale, Qt
        from PySide6.QtWidgets import QApplication
    return QApplication, QLocale, Qt


def _import_app_modules():
    """Import sibling modules without depending on this folder's name."""
    if __package__ not in (None, ""):
        from . import i18n
        from .main_window import MainWindow

        return i18n, MainWindow

    package = types.ModuleType(_DYNAMIC_PACKAGE)
    package.__path__ = [str(Path(__file__).resolve().parent)]  # type: ignore[attr-defined]
    package.__package__ = _DYNAMIC_PACKAGE
    sys.modules[_DYNAMIC_PACKAGE] = package
    i18n = importlib.import_module(f"{_DYNAMIC_PACKAGE}.i18n")
    main_window = importlib.import_module(f"{_DYNAMIC_PACKAGE}.main_window")
    return i18n, main_window.MainWindow


def main() -> None:
    QApplication, QLocale, Qt = _import_pyside6()
    i18n, MainWindow = _import_app_modules()

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    # macOS native style ignores much of QSS and leaves awkward grey chrome on tab bars;
    # Fusion paints widgets consistently so our dark theme applies everywhere.
    app.setStyle("Fusion")
    app.setOrganizationName("StateTuning")
    app.setApplicationName("pyside_desktop")
    i18n.load_messages()
    saved = i18n.load_saved_locale()
    i18n.set_locale(saved or i18n.resolve_locale_from_system(QLocale.system()))
    win = MainWindow()
    win.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
