import os
import allure
import pytest
import logging
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.appium_service import AppiumService
from Utilities.EmulatorWindow import bring_emulator_to_front
from Utilities.ErrorDiagnostics import format_error, preflight_problems

# Initialize logger for conftest tracking
log = logging.getLogger(__name__)

# IDEs launched from the desktop don't read ~/.bashrc, so Appium wouldn't find the Android SDK
if not (os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")):
    os.environ["ANDROID_HOME"] = os.path.expanduser("~/Android/Sdk")


# --- PYTEST REPORTING HOOK ---
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


# --- APPIUM SERVICE FIXTURE ---
@pytest.fixture(scope="session")
def appium_service_start_stop():
    """Starts the Appium service before the test session and stops it afterward."""
    appium_service = AppiumService()
    log.info("Starting Appium Service...")
    try:
        appium_service.start(timeout_ms=30000)
    except Exception as e:
        log.error(format_error(e, "Appium service"))
        raise
    yield appium_service
    if appium_service.is_running:
        log.info("Stopping Appium Service...")
        appium_service.stop()


# --- HELPER: COMMON CAPABILITIES ---
def get_common_options():
    options = AppiumOptions()
    options.set_capability('platformName', 'Android')
    options.set_capability('deviceName', 'emulator-5554')
    options.set_capability('automationName', 'UiAutomator2')
    options.set_capability('app', os.environ.get('APP_APK_PATH', os.path.expanduser('~/apk/826.apk')))
    options.set_capability('appPackage', 'com.lernr.app')
    options.set_capability('appActivity', '.ui.splash.SplashActivity')
    options.set_capability('appWaitActivity', 'com.lernr.app.*')
    options.set_capability('appWaitDuration', 45000)  # Increased to 45s for slow loading

    # --- CLEANUP & STABILITY IMPROVEMENTS ---
    options.set_capability('noReset', False)  # Forces clear of app cache/data every run
    options.set_capability('fullReset', False)  # Keeps app installed but wipes it clean
    options.set_capability('autoGrantPermissions', True)
    options.set_capability('noSign', True)  # Skips resign step to speed up launch

    # --- TIMEOUT OPTIMIZATIONS ---
    options.set_capability('newCommandTimeout', 600)  # Increased to 10 mins for long waits
    options.set_capability('adbExecTimeout', 120000)  # Increased to 120s for slow MBP emulators
    options.set_capability('androidInstallTimeout', 120000)
    return options


# --- HELPER: FAILURE SCREENSHOT ---
def attach_failure_screenshot(item, driver):
    """Attaches a screenshot to Allure if the test failed. Must run while the session is still alive."""
    if not (hasattr(item, 'rep_call') and item.rep_call.failed) or getattr(item, '_screenshot_done', False):
        return
    item._screenshot_done = True
    try:
        allure.attach(driver.get_screenshot_as_png(), name="failure_screenshot", attachment_type=AttachmentType.PNG)
        log.info("Screenshot captured and attached to Allure report.")
    except Exception as e:
        log.warning(f"Screenshot skipped: {format_error(e)}")


# --- HELPER: SESSION CREATION WITH READABLE ERRORS ---
def create_driver(options):
    """Runs pre-flight checks, then starts the session; logs a clear cause + fix on failure."""
    problems = preflight_problems(options.get_capability('app'), options.get_capability('deviceName'))
    for problem in problems:
        log.error(f"PRE-FLIGHT: {problem}")
    if problems:
        pytest.fail("Environment not ready:\n  - " + "\n  - ".join(problems), pytrace=False)
    bring_emulator_to_front()  # emulator may be hidden/minimized behind other windows
    try:
        driver = webdriver.Remote('http://localhost:4723', options=options)
        bring_emulator_to_front()  # app install/launch can push the window back
        return driver
    except Exception as e:
        log.error(format_error(e, "Session start"))
        pytest.fail(format_error(e, "Session start"), pytrace=False)


# --- APPIUM DRIVER FIXTURE (Standard - Resets every test) ---
@pytest.fixture(scope="function")
def appium_driver(request, appium_service_start_stop):
    options = get_common_options()
    options.set_capability('noReset', False)  # Clears app data for clean state

    log.info("Initializing Standard Remote WebDriver session...")
    driver = create_driver(options)
    if request.cls:
        request.cls.driver = driver
    driver.implicitly_wait(10)
    yield driver
    attach_failure_screenshot(request.node, driver)  # before quit, otherwise the session is gone
    log.info("Quitting Standard WebDriver session.")
    driver.quit()


# --- CONTINUOUS DRIVER FIXTURE (E2E - Keeps app state) ---
@pytest.fixture(scope="class")
def appium_driver_continuous(request, appium_service_start_stop):
    """Initializes driver ONCE per class. Used for Step 1 -> Step 2 -> Step 3."""
    options = get_common_options()
    options.set_capability('noReset', True)  # IMPORTANT: Prevents app from clearing data

    log.info("🚀 Starting CONTINUOUS session for E2E flow...")
    driver = create_driver(options)

    if request.cls:
        request.cls.driver = driver

    driver.implicitly_wait(10)
    yield driver
    log.info("🏁 Ending CONTINUOUS session.")
    driver.quit()


# --- LOG ON FAILURE FIXTURE ---
@pytest.fixture(autouse=True)
def log_on_failure(request):
    yield
    item = request.node
    if hasattr(item, 'rep_call') and item.rep_call.failed:
        driver = getattr(item.instance, 'driver', None)
        if driver:
            log.error(f"!!! TEST FAILED: {item.nodeid} !!!")
            attach_failure_screenshot(item, driver)  # no-op if the driver fixture already did it
