from Pages.BasePage import BasePage

class dailyDppScreen(BasePage):
    def __init__(self,driver):
        super().__init__(driver)

    def dailyDpp(self):
        #start test and go to question page
        self.click("dailyDpp_StartTest_XPATH")
        #seelct correct options from question page
        self.click("selectCorrectOptionBy_ID")
        #go to the next question page
        self.click("next_question_XPATH")