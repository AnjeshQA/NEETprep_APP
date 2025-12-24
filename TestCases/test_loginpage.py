import pytest
from Pages.HomeScreen import HomeScreen
from Pages.dailyDppScreen import dailyDppScreen
from Pages.loginScreen import loginScreen
from TestCases.BaseTest import BaseTest
from Utilities import dataProvider


class Test_LoginPage(BaseTest):

    @pytest.mark.parametrize("mobileNumber, otp", dataProvider.get_data("UserDetail"))
    def test_login_Logout_Page(self, mobileNumber, otp):
        login = loginScreen(self.driver)
        login.gotoLoggedIn(mobileNumber, otp).gotoLogout()

    # @pytest.mark.parametrize("mobileNumber, otp", dataProvider.get_data("UserDetail"))
    # def test_loginPage(self, mobileNumber, otp):
    #     login = loginScreen(self.driver)
    #     login.gotoLoggedIn(mobileNumber, otp).gotoDailyDpp()
