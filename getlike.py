from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import configparser


# 你的 Twitter 账号信息
TWITTER_USERNAME = "yinmou19"
TWITTER_PASSWORD = "nbyqy123"
TWITTER_EMAIL_OR_PHONE = "amusingyyy@gmail.com"
# 配置 Microsoft Edge WebDriver


options = webdriver.EdgeOptions()
options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/121.0.0.0 Safari/537.36")
# options.add_argument("--headless")
driver = webdriver.Edge(options=options)


try:
    # 打开 Twitter 登录页面
    driver.get("https://twitter.com/login")
    time.sleep(5)
    print(driver.title)
    # 输入用户名
    # username_input = driver.find_element(By.NAME, "text")
    username_input = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')

    username_input.send_keys(TWITTER_USERNAME)
    username_input.send_keys(Keys.RETURN)
    time.sleep(3)

    # 可能需要输入邮箱或手机号
    # email_input = driver.find_element(By.NAME, "text")
    try:
        email_or_phone_input = driver.find_element(By.XPATH, '//input[@name="text"]')
        email_or_phone_input.send_keys(TWITTER_EMAIL_OR_PHONE)
        email_or_phone_input.send_keys(Keys.RETURN)
        time.sleep(3)
    except:
        print("No email or phone input found.")

    # 输入密码
    # password_input = driver.find_element(By.NAME, "password")
    password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
    password_input.send_keys(TWITTER_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(3)

    # 访问点赞页面
    driver.get(f"https://twitter.com/{TWITTER_USERNAME}/likes")
    time.sleep(3)

    # 获取所有点赞的推文
    # tweets = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')
    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    # 获取文本内容
    for tweet in tweets:
        try:
            text = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
        except:
            text = "(无文本)"

        # 获取图片 URL
        images = tweet.find_elements(By.XPATH, './/img[contains(@src, "twimg.com/media")]')
        image_urls = [img.get_attribute("src") for img in images]

        print("\n📌 推文内容:", text)
        if image_urls:
            print("🖼️ 图片:", image_urls)

finally:
    driver.quit()
