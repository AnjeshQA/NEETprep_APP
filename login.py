import time
from appium import webdriver
from typing import Any, Dict
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Capabilities
cap: Dict[str, Any] = {
    "automationName": "UiAutomator2",
    "platformName": "Android",
    "deviceName": "Android"
}

url = 'http://localhost:4723'
driver = webdriver.Remote(url, options=AppiumOptions().load_capabilities(cap))

# Implicit wait
driver.implicitly_wait(20)

# Initialize WebDriverWait
wait = WebDriverWait(driver, 20)

# Click on "Predicted app: NEETprep"
el = driver.find_element(by=AppiumBy.XPATH, value='//android.widget.TextView[@content-desc="Predicted app: NEETprep"]')
el.click()

time.sleep(2)

# Fill phone number field
el = driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText[@resource-id="com.lernr.app:id/authInput"]')
el.send_keys("9000000000")

# Click on Send OTP button
driver.find_element(by=AppiumBy.XPATH, value='//androidx.cardview.widget.CardView[@resource-id="com.lernr.app:id/SendOTP"]/android.widget.LinearLayout').click()

# Enter password
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText[@resource-id="com.lernr.app:id/password"]').send_keys('876302')

# Click on Verify OTP button
driver.find_element(by=AppiumBy.XPATH, value='//androidx.cardview.widget.CardView[@resource-id="com.lernr.app:id/VerifyOTP"]/android.widget.LinearLayout').click()

# Scroll down within an element (FrameLayout)
elements = driver.find_elements(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.lernr.app:id/physics_card"]/android.widget.LinearLayout')
if len(elements) > 0:
    elements[0].click()
else:
    print("Element not found!")

time.sleep(100)
driver.quit()
# Scroll down in the specified element
driver.execute_script('mobile: scroll', {'direction': 'down', 'element': elements})

time.sleep(30)
# Click on the physics card
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.lernr.app:id/physics_card"]/android.widget.LinearLayout').click()

# Click on a chapter link
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.TextView[@resource-id="com.lernr.app:id/chapter_small_cardview_text" and @text="Units and Measurement"]').click()

# Click on "Practice Questions (Deprecated)"
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.TextView[@text="Practice Questions (Deprecated)"]').click()

# Click on "Show me in NCERT"
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@resource-id="com.lernr.app:id/show_me_in_ncert"]').click()

# Close the NCERT view
driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="com.lernr.app:id/touch_outside"]').click()

# Click on the back button in the toolbar
driver.find_element(by=AppiumBy.XPATH, value='//android.view.ViewGroup[@resource-id="com.lernr.app:id/toolbar_question"]/android.widget.ImageButton').click()

# Click on the ImageButton
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.ImageButton').click()

# Navigate up
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.ImageButton[@content-desc="Navigate up"]').click()

# Click on another ImageButton
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.ImageButton').click()

# Click on the first tab icon
driver.find_element(by=AppiumBy.XPATH, value='(//android.widget.ImageView[@resource-id="com.lernr.app:id/tab_icon"])[1]').click()

# Click on "Button1" to confirm the action
driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@resource-id="android:id/button1"]').click()

# Sleep to see the result before quitting
time.sleep(10)

# Quit
