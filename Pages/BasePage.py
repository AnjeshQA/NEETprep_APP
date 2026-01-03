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


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # 30s timeout is good for emulators to handle transitions/splash screens
        self.wait = WebDriverWait(self.driver, 30, poll_frequency=1)

    def get_element(self, locator):
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
            element = self.wait.until(EC.visibility_of_element_located((by, locator_value)))
            return element
        except TimeoutException:
            log.logger.error(f"FAIL: Element '{locator}' not visible after 30s at: {locator_value}")
            raise
        except Exception as e:
            log.logger.error(f"Unexpected error finding '{locator}': {str(e)}")
            raise

    def click(self, locator):
        """Clicks an element after logging the attempt."""
        log.logger.info(f"Step: Clicking on Element -> {locator}")
        element = self.get_element(locator)
        element.click()

    def type(self, locator, value):
        """Clears, types, and hides keyboard after logging the attempt."""
        log.logger.info(f"Step: Typing '{value}' into -> {locator}")
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

    def is_element_present(self, locator):
        """Checks presence without raising an exception; useful for conditional logic."""
        try:
            # Use shorter wait for 'check' only logic
            WebDriverWait(self.driver, 5).until(lambda d: self.get_element(locator))
            return True
        except:
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