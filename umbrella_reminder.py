####################################################################
# Python x AI Agent
# Selenium, XPath, SMS - 網路爬蟲、簡訊
#
# [專案]
# 攜帶雨具
# 問題：請詳閱附件 ReadMe_umbrella_reminder.pdf 說明
#       撰寫程式可登入氣象台網站，爬取明日降雨機率預報。
#       如果高於設定的機率，則程式會自動傳送提醒簡訊。
#
# 輸入：中央氣象台網站
#       (https://www.cwa.gov.tw/V8/C/W/County/index.html)
#
# 輸出：
#    如果降雨機率高於設定值(如：35%)，則程式會自動傳送手機
#    簡訊給你，提醒記得攜帶雨具，並告知預報之降雨機率值
#####################################################################

# Before running, please install necessary libraries:
# pip install selenium webdriver-manager twilio

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

def rain_chance(url, city='臺北市', threshold=35):
    """
    進入氣象台網址的正確網頁爬取明日降雨機率，如果高於臨界值
    (threshold) 則傳回此降雨機率。
    :param str url: 氣象台網址
    :param str city: 縣市名稱
    :param int threshold: 降雨機率，如果高於臨界值
    :return int: None (若低於臨界值) / 降雨機率
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        # Wait for the city selection link to be clickable and click it
        city_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, city))
        )
        city_link.click()

        # Wait for the weekly forecast table to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PC_week"))
        )

        # XPath to get tomorrow's rain probability.
        # This selects the first row (tomorrow) in the weekly forecast table,
        # then the 4th cell (PoP), and gets the numeric value from the span.
        rain_prob_xpath = '//div[@id="PC_week"]//tbody/tr[1]/td[4]/span'
        
        rain_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, rain_prob_xpath))
        )

        rain_prob_text = rain_element.text
        # The text is like "80 %", we need to extract the number
        rain_prob = int(rain_prob_text.split(' ')[0])

        if rain_prob >= threshold:
            return rain_prob
        else:
            return None

    except Exception as e:
        print(f"An error occurred while scraping: {e}")
        return None
    finally:
        driver.quit()

def textme(message):
    """
    登入 twilio 伺服器，並依傳入參數 (message 訊息內容)
    傳送手機簡訊給自己。。
    :param str message: 要傳送的訊息，含降雨機率
    """
    # !!! IMPORTANT !!!
    # Replace the placeholder values below with your actual Twilio credentials and numbers.
    # You can find your Account SID and Auth Token at twilio.com/console
    account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your Account SID
    auth_token = 'your_auth_token'              # Replace with your Auth Token
    twilio_phone_number = '+15017122661'        # Replace with your Twilio phone number
    your_phone_number = '+886123456789'         # Replace with your phone number

    try:
        client = Client(account_sid, auth_token)
        sms = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=your_phone_number
        )
        print(f"Message sent successfully! SID: {sms.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        print("Please ensure your Twilio credentials and phone numbers are set correctly in the textme() function.")


if __name__ == "__main__":
    CWA_URL = "https://www.cwa.gov.tw/V8/C/W/County/index.html"
    # You can change this to your city, e.g., "新北市", "臺中市", "高雄市"
    TARGET_CITY = "臺北市"
    # Set your desired rain probability threshold (%)
    RAIN_THRESHOLD = 35

    print(f"Checking tomorrow's rain probability for {TARGET_CITY}...")
    probability = rain_chance(CWA_URL, city=TARGET_CITY, threshold=RAIN_THRESHOLD)

    if probability is not None:
        print(f"Rain probability is {probability}%, which is at or above the threshold of {RAIN_THRESHOLD}%.")
        message_body = f"Rain alert! Tomorrow's chance of precipitation in {TARGET_CITY} is {probability}%. Don't forget to take an umbrella!"
        print("Sending SMS notification...")
        textme(message_body)
    else:
        print(f"Tomorrow's rain probability is below the threshold of {RAIN_THRESHOLD}%. No notification sent.")