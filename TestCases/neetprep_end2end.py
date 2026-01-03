import pytest
from Pages.HomeScreen import HomeScreen
from Pages.dailyDppScreen import dailyDppScreen
from Pages.loginScreen import loginScreen
from TestCases.BaseTest import BaseTest
from Utilities import dataProvider


# Use the continuous fixture so the app doesn't restart between steps
@pytest.mark.usefixtures("appium_driver_continuous")
@pytest.mark.parametrize("mobileNumber, otp", dataProvider.get_data("UserDetail"))
class Test_NeetPrep_EndToEnd(BaseTest):

    def test_01_login_step(self, appium_driver_continuous, mobileNumber, otp):
        """Step 1: Handle the login process."""
        self.login = loginScreen(self.driver)
        print(f"Starting Login with: {mobileNumber}")

        # This performs the phone entry and OTP verification
        self.login.gotoLoggedIn(mobileNumber, otp)

    def test_02_navigate_to_dpp(self, appium_driver_continuous, mobileNumber, otp):
        """Step 2: Start from Home and navigate to Daily DPP."""
        # The app is already logged in from the previous step
        self.home = HomeScreen(self.driver)
        print("Navigating to Daily DPP...")

        self.home.gotoDailyDpp()

    def test_03_perform_dpp_actions(self, appium_driver_continuous, mobileNumber, otp):
        """Step 3: Perform actions on the Daily DPP screen."""
        # The app is already on the Daily DPP screen
        self.dpp = dailyDppScreen(self.driver)
        print("Executing Daily DPP test logic...")

        self.dpp.dailyDpp()