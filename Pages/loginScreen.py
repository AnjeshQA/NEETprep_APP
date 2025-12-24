from time import sleep

from Pages.BasePage import BasePage
from Pages.HomeScreen import HomeScreen


class loginScreen(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # Added arguments to receive data from the test
    def gotoLoggedIn(self, mobileNumber, otp):
        # 1. OPTIONAL: Handle 'Get Started' if it exists (fresh install)
        # If your app has a 'Next' or 'Get Started' button first, add it here:
        # if self.is_element_present("get_started_ID"):
        #     self.click("get_started_ID")

        # 2. Type Mobile Number
        # BasePage now uses 'visibility_of_element_located', so it will wait
        # for the splash screen to disappear automatically.
        self.type("mobile_number_ID", mobileNumber)

        # 3. Request OTP
        self.click("otpButton_ID")

        # 4. Handle OTP - sometimes the field takes a moment to appear after clicking
        self.type("enterOTP_ID", otp)
        self.click("verifyOTP_ID")
        sleep(10)
        return HomeScreen(self.driver)

