from time import sleep
from Pages.BasePage import BasePage
from Pages.HomeScreen import HomeScreen


class loginScreen(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    def gotoLoggedIn(self, mobileNumber, otp):
        # 1. Type Mobile Number
        self.type("mobile_number_ID", mobileNumber)

        # 2. Hide Keyboard (Ensures the checkbox and buttons are reachable)
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()

        # 3. Checkbox T&C
        self.click("term_Condition_Checkbox_ID")

        # 4. Request OTP
        self.click("otpButton_ID")

        # 5. Handle OTP
        self.type("enterOTP_ID", otp)

        # Give the UI a moment to register the OTP input before swiping
        sleep(2)

        # 6. COORDINATE FIX: Swipe Up (Pixel 5: 1080x2340)
        # Pulls the 'Verify OTP' button from the bottom edge to the center
        self.driver.swipe(540, 1800, 540, 600, 1000)

        # 7. Verify and Proceed
        self.click("verifyOTP_ID")

        # Return the next page object
        return HomeScreen(self.driver)