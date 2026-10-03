"""Turns raw Appium/Selenium/pytest failures into short, actionable log messages."""
import os
import re
import shutil
import subprocess

# (regex on the error text, headline, how to fix) - first match wins
_KNOWN_ERRORS = [
    (r"application at '(?P<p>[^']+)' does not exist",
     "APK not found: {p}",
     "Check the 'app' capability in conftest.py or set APP_APK_PATH=/path/to/app.apk"),
    (r"Neither ANDROID_HOME nor ANDROID_SDK_ROOT",
     "Android SDK not found (ANDROID_HOME / ANDROID_SDK_ROOT not set)",
     "export ANDROID_HOME=$HOME/Android/Sdk (IDE launched from desktop does not read ~/.bashrc)"),
    (r"Could not find a connected Android device|device .* not found|no devices/emulators found",
     "No Android device/emulator connected",
     "Start the emulator or plug in the device, then confirm with: adb devices"),
    (r"Connection refused.*4723|connect ECONNREFUSED.*4723",
     "Appium server is not reachable on port 4723",
     "Start Appium (appium) or check that the port is not used by another process"),
    (r"Activity .* does not exist|Cannot start the '.*' application|appActivity",
     "App launch failed: wrong appPackage/appActivity or app crashed on start",
     "Verify appPackage/appActivity match the installed APK (adb shell dumpsys package <pkg>)"),
    (r"INSTALL_FAILED_(?P<r>\w+)",
     "APK install failed: {r}",
     "Uninstall the old app (adb uninstall com.lernr.app) or free emulator storage"),
    (r"session is either terminated or not started",
     "Driver session already ended (app/emulator crashed or session timed out)",
     "Check the earlier error in this log - this is usually a side effect"),
]


def diagnose(exc) -> tuple[str, str]:
    """Return (headline, hint) for an exception. Falls back to its first message line."""
    text = str(exc)
    for pattern, headline, hint in _KNOWN_ERRORS:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            return headline.format(**m.groupdict()), hint
    first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), type(exc).__name__)
    return f"{type(exc).__name__}: {first_line[:200]}", "See full traceback below"


def format_error(exc, context="") -> str:
    headline, hint = diagnose(exc)
    prefix = f"[{context}] " if context else ""
    return f"{prefix}{headline}\n    -> FIX: {hint}"


def preflight_problems(apk_path, device_name=None) -> list[str]:
    """Cheap local checks run before starting a session; returns a list of problems."""
    problems = []
    if not os.path.isfile(apk_path):
        problems.append(f"APK not found: {apk_path}  -> set APP_APK_PATH or fix 'app' in conftest.py")
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk or not os.path.isdir(sdk):
        problems.append(f"Android SDK folder not found: {sdk}  -> set ANDROID_HOME")
    adb = shutil.which("adb") or (os.path.join(sdk, "platform-tools", "adb") if sdk else None)
    if adb and os.path.exists(adb):
        try:
            out = subprocess.run([adb, "devices"], capture_output=True, text=True, timeout=15).stdout
            devices = [ln.split()[0] for ln in out.splitlines()[1:] if ln.strip().endswith("device")]
            if not devices:
                problems.append("No Android device/emulator connected  -> start emulator, check: adb devices")
            elif device_name and device_name not in devices:
                problems.append(f"Device '{device_name}' not connected (found: {', '.join(devices)})")
        except Exception as e:  # adb hanging/missing must not block the run
            problems.append(f"Could not run 'adb devices': {e}")
    else:
        problems.append("adb not found  -> install platform-tools / add to PATH")
    return problems
