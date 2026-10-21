import logging
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from Utilities.LogUtil import Logger
from Utilities import configReader

# Initialize Logger using your custom Logger utility
log = Logger(__name__, logging.INFO)

# Values typed into locators whose name contains one of these words are never written to logs
_SENSITIVE_WORDS = ("otp", "password", "pwd")

# Must match driver.implicitly_wait() in TestCases/conftest.py
IMPLICIT_WAIT = 10


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # 30s timeout is good for emulators to handle transitions/splash screens
        self.wait = WebDriverWait(self.driver, 30, poll_frequency=1)

    def get_element(self, locator, timeout=None, log_failure=True):
        """Returns a visible element. `timeout` overrides the default 30s wait; log_failure=False
        suppresses the ERROR log (used by presence checks where absence is an expected outcome)."""
        locator_value = configReader.readConfig("locators", locator)

        # Mapping suffixes to AppiumBy strategies
        if str(locator).endswith("_XPATH"):
            by = AppiumBy.XPATH
        elif str(locator).endswith("_ACCESSIBILITYID"):
            by = AppiumBy.ACCESSIBILITY_ID
        elif str(locator).endswith("_ID"):
            by = AppiumBy.ID
        elif str(locator).endswith("_UIAUTOMATOR"):
            by = AppiumBy.ANDROID_UIAUTOMATOR
        else:
            log.logger.error(f"Invalid locator suffix for: {locator}")
            return None

        try:
            # Visibility check is more reliable than presence for interaction
            if timeout is None:
                return self.wait.until(EC.visibility_of_element_located((by, locator_value)))
            # Short, optional-element lookups: the global implicitly_wait(10) would stretch every poll
            # to 10s, so disable it for the duration of this explicit wait and restore it afterwards.
            self.driver.implicitly_wait(0)
            try:
                wait = WebDriverWait(self.driver, timeout, poll_frequency=0.5)
                return wait.until(EC.visibility_of_element_located((by, locator_value)))
            finally:
                self.driver.implicitly_wait(IMPLICIT_WAIT)
        except TimeoutException:
            if log_failure:
                log.logger.error(f"FAIL: Element '{locator}' not visible after {timeout or 30}s at: {locator_value}")
            raise
        except Exception as e:
            log.logger.error(f"Unexpected error finding '{locator}': {str(e)}")
            raise

    def click(self, locator, timeout=None):
        """Clicks an element after logging the attempt. Pass a small `timeout` for optional elements."""
        log.logger.info(f"Step: Clicking on Element -> {locator}")
        element = self.get_element(locator, timeout=timeout, log_failure=timeout is None)
        element.click()

    def click_if_present(self, locator, timeout=3):
        """Clicks the element if it shows up within `timeout` seconds. Returns True if clicked, else False."""
        try:
            self.click(locator, timeout=timeout)
            return True
        except Exception:
            log.logger.info(f"Optional element '{locator}' not found within {timeout}s, skipping")
            return False

    def type(self, locator, value):
        """Clears, types, and hides keyboard after logging the attempt."""
        shown = "****" if any(w in str(locator).lower() for w in _SENSITIVE_WORDS) else value
        log.logger.info(f"Step: Typing '{shown}' into -> {locator}")
        element = self.get_element(locator)
        element.clear()
        element.send_keys(str(value))

        # Hide keyboard to prevent it from overlapping other elements
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
                log.logger.info("Keyboard hidden successfully.")
        except Exception:
            pass

    def is_element_present(self, locator, timeout=5):
        """Returns True if the element becomes visible within `timeout` seconds, else False. Never raises."""
        try:
            self.get_element(locator, timeout=timeout, log_failure=False)
            log.logger.info(f"Check: '{locator}' is visible")
            return True
        except Exception:
            log.logger.warning(f"Check: '{locator}' not visible after {timeout}s")
            return False

    def scroll_to_bottom_fast(self):
        """
        Direct approach: Swipes once to the bottom of the scrollable container.
        This stops the 'up and down' jumping.
        """
        try:
            # Hide keyboard if it's blocking the view
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()

            # Native command to scroll to the very end of the page instantly
            self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                     'new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollToEnd(1);')
            return True
        except Exception:
            # Fallback: if native fails, do one big manual swipe
            size = self.driver.get_window_size()
            self.driver.swipe(size['width'] * 0.5, size['height'] * 0.8, size['width'] * 0.5, size['height'] * 0.2, 500)