import allure
from Pages.BasePage import BasePage, log
from Pages.dailyDppScreen import dailyDppScreen


class HomeScreen(BasePage):
    def __init__(self,driver):
        super().__init__(driver)

    def gotoDailyDpp(self):
        self.click("dailyDpp_XPATH")
        return dailyDppScreen(self.driver)

    def gotoLogout(self):
        self.click("drawerMenu_XPATH")

        self.click("logoutButton_UIAUTOMATOR")

        self.click("logoutConfirmation_ID")

        # Verify the user is logged out and redirected to the login screen
        with allure.step("Verify user is redirected to the login screen after logout"):
            assert self.is_element_present("mobile_number_ID"), \
                "Logout failed: login screen (mobile number field) not shown within 5s after logout"
            log.logger.info("Logout verified: redirected to the login screen")
        return self