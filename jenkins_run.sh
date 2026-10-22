#!/usr/bin/env bash
# Jenkins build step (Linux). Jenkins already checks out the repo, so no git commands here.
# Required env: TEST_MOBILE, TEST_OTP (bind as secret text in the job).
# Optional env: APP_APK_PATH (default ~/apk/826.apk), ANDROID_HOME, AVD_NAME (default Medium_Phone).
set -euo pipefail

export ANDROID_HOME="${ANDROID_HOME:-/home/anjesh-chauhan/Android/Sdk}"
export PATH="/usr/local/bin:/usr/bin:/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
export APP_APK_PATH="${APP_APK_PATH:-/home/anjesh-chauhan/apk/826.apk}"

: "${TEST_MOBILE:?TEST_MOBILE is not set}"
: "${TEST_OTP:?TEST_OTP is not set}"
[ -f "$APP_APK_PATH" ] || { echo "APK not found: $APP_APK_PATH"; exit 1; }

# Virtual environment + dependencies (the file is spelled requirments.txt)
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirments.txt

# Start a headless emulator only if no device is connected
if ! adb devices | grep -qw device; then
    echo "No device connected, starting emulator ${AVD_NAME:-Medium_Phone}..."
    nohup emulator -avd "${AVD_NAME:-Medium_Phone}" -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim >emulator.log 2>&1 &
    adb wait-for-device
    until [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do sleep 5; done
fi

rm -rf allure-results
python -m pytest TestCases/test_loginpage.py --alluredir=allure-results --reruns 1

# Jenkins job setup:
#   Build step: Execute shell -> bash jenkins_run.sh
#   Environment: Use secret text(s) -> TEST_MOBILE, TEST_OTP
#   Post-build: Allure Report -> allure-results
