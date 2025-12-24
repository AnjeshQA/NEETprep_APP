import time

import pytest
from appium import webdriver
from appium.webdriver.appium_service import AppiumService


def get_data():
    return [

        ["Delhi"],
        ["Dubai"],

    ]


def setup_function():
    global appium_service
    appium_service = AppiumService()
    appium_service.start()

    desired_caps = {}
    desired_caps['platformName'] = 'Android'
    desired_caps['deviceName'] = 'Android'
    desired_caps['appPackage'] = 'com.goibibo'
    desired_caps['appActivity'] = '.common.HomeActivity'
    desired_caps['noReset'] = True
    global driver
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    driver.implicitly_wait(10)


def teardown_function():
    time.sleep(2)
    driver.quit()
    appium_service.stop()


@pytest.mark.parametrize("city", get_data())
def test_dologin(city):
    driver.find_element_by_id('com.goibibo:id/btn1').click()
    driver.find_element_by_accessibility_id('destination').click()
    driver.find_element_by_id('com.goibibo:id/edtSearch').send_keys(city)
    driver.find_elements_by_id('com.goibibo:id/lytLocationItem')[0].click()
    driver.find_element_by_xpath("//android.widget.TextView[@text='Search']").click()
    cityText = driver.find_element_by_xpath("//android.widget.TextView[contains(@text,'EXPLORE')]").text
    print(cityText)
    newCityText = str(cityText).replace("EXPLORE ", "").replace("!", "")
    print(newCityText)

    assert newCityText in str(city).upper()