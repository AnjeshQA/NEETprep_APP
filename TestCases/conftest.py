import allure
import pytest
import logging
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.appium_service import AppiumService

# Initialize logger for conftest tracking
log = logging.getLogger(__name__)


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
    appium_service.start(timeout_ms=30000)
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
    options.set_capability('app', '/Applications/APK/apprelease.apk')
    options.set_capability('appPackage', 'com.lernr.app')
    options.set_capability('appActivity', '.ui.splash.SplashActivity')
    options.set_capability('appWaitActivity', 'com.lernr.app.*')
    options.set_capability('appWaitDuration', 30000)
    options.set_capability('autoGrantPermissions', True)
    options.set_capability('newCommandTimeout', 300)
    options.set_capability('adbExecTimeout', 90000)
    return options


# --- APPIUM DRIVER FIXTURE (Standard - Resets every test) ---
@pytest.fixture(scope="function")
def appium_driver(request, appium_service_start_stop):
    options = get_common_options()
    options.set_capability('noReset', False)  # Clears app data for clean state

    log.info("Initializing Standard Remote WebDriver session...")
    driver = webdriver.Remote('http://localhost:4723', options=options)
    if request.cls:
        request.cls.driver = driver
    driver.implicitly_wait(10)
    yield driver
    log.info("Quitting Standard WebDriver session.")
    driver.quit()


# --- CONTINUOUS DRIVER FIXTURE (E2E - Keeps app state) ---
@pytest.fixture(scope="class")
def appium_driver_continuous(request, appium_service_start_stop):
    """Initializes driver ONCE per class. Used for Step 1 -> Step 2 -> Step 3."""
    options = get_common_options()
    options.set_capability('noReset', True)  # IMPORTANT: Prevents app from clearing data

    log.info("🚀 Starting CONTINUOUS session for E2E flow...")
    driver = webdriver.Remote('http://localhost:4723', options=options)

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
            try:
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, name="failure_screenshot", attachment_type=AttachmentType.PNG)
                log.info("Screenshot captured and attached to Allure report.")
            except Exception as e:
                log.error(f"Failed to capture screenshot: {e}")