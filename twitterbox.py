from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import configparser

class TwitterBox:
    def __init__(self, config):
        # init config
        self.username = config['account']['username']
        self.email_or_phone = config['account']['email_or_phone']
        self.password = config['account']['password']
        self.browser = config['browser']['browser']
        self.headless = config['browser']['headless']
        self.user_agent = config['browser']['user_agent']
        self.max_post_num = config['bot']['max_post_num']
        self.refresh_interval = config['bot']['refresh_interval']
        self.filter_tags = config['bot']['filter_tags']
        self.trigger = config['bot']['trigger']
        self.save_path = config['bot']['save_path']

        # init driver
        self.options = None
        self.driver = None

        if self.browser == 'edge':
            self.options = webdriver.EdgeOptions()
        elif self.browser == 'chrome':
            self.options = webdriver.ChromeOptions()
        elif self.browser == 'firefox':
            self.options = webdriver.FirefoxOptions()
        else:
            raise Exception('Unsupported browser')
        
        self.options.add_argument(self.user_agent)
        if self.headless:
            self.options.add_argument("--headless")

        if self.browser == 'edge':
            self.driver = webdriver.Edge(options=self.options)
        elif self.browser == 'chrome':
            self.driver = webdriver.Chrome(options=self.options)
        elif self.browser == 'firefox':
            self.driver = webdriver.Firefox(options=self.options)
        else:
            raise Exception('Unsupported browser')
    
    def __del__(self):
        self.driver.quit()

    def run(self):
        try:
            self._login()
            while True:
                self._get_likes()
                time.sleep(self.refresh_interval)
        except Exception as e:
            print('Bot stopped running. Error occured:',e)
            return
        driver = self.driver
        TWITTER_USERNAME = self.username
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
    
    def _login(self):
        driver = self.driver
        TWITTER_USERNAME = self.username
        TWITTER_EMAIL_OR_PHONE = self.email_or_phone
        TWITTER_PASSWORD = self.password

        driver.get("https://twitter.com/login")
        time.sleep(5)

        # input username
        username_input = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')
        username_input.send_keys()
        username_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # input email or phone if needed
        try:
            email_or_phone_input = driver.find_element(By.XPATH, '//input[@name="text"]')
            email_or_phone_input.send_keys(TWITTER_EMAIL_OR_PHONE)
            email_or_phone_input.send_keys(Keys.RETURN)
            time.sleep(3)
        except:
            print("No email or phone input found.")

        # input password
        password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
        password_input.send_keys(TWITTER_PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)


