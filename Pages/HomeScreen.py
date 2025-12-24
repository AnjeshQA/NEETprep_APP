from Pages.BasePage import BasePage
from Pages.dailyDppScreen import dailyDppScreen


class HomeScreen(BasePage):
    def __init__(self,driver):
        super().__init__(driver)

    def gotoDailyDpp(self):
        self.click("dailyDpp_XPATH")
        return dailyDppScreen(self.driver)

    def gotoLogout(self):
        self.click("drawerMenu_XPATH")

        self.click("logoutButton_ID")

        self.click("logoutConfirmation_ID")