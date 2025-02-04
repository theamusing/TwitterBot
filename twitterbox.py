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
        self.max_post_num = config['bot']['max_posts']
        self.refresh_interval = config['bot']['refresh_interval']
        self.filter_tags = config['bot']['filter_tags']
        self.trigger = config['bot']['trigger']
        self.save_path = config['bot']['save_path']

        self.last_post_id = None

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
                self._get_likes(self.max_post_num)
                time.sleep(self.refresh_interval)
        except Exception as e:
            print('Bot stopped running. Error occured:',e)
            return
    
    def _login(self):
        driver = self.driver
        TWITTER_USERNAME = self.username
        TWITTER_EMAIL_OR_PHONE = self.email_or_phone
        TWITTER_PASSWORD = self.password

        driver.get("https://twitter.com/login")
        time.sleep(5)

        # input username
        username_input = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')
        username_input.send_keys(TWITTER_USERNAME)
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

    def _get_likes(self, max_post_num):
        driver = self.driver
        TWITTER_USERNAME = self.username

        print("Fetching liked tweets...")
        driver.get(f"https://twitter.com/{TWITTER_USERNAME}/likes")
        time.sleep(5)

        liked_tweets = []
        collected_tweet_ids = []
        scroll_attempts = 0
        max_scrolls = 100 

        while len(liked_tweets) < max_post_num and scroll_attempts < max_scrolls:
            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            for tweet in tweets:

                # get tweet id
                tweet_link = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]').get_attribute("href")
                tweet_id = tweet_link.split("/")[-1] 

                if(tweet_id == self.last_post_id):
                    scroll_attempts = max_scrolls # stop scrolling
                    break

                if tweet_id in collected_tweet_ids:
                    continue 
                
                # get text content
                try:
                    text = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                except:
                    text = ""

                # get images URLs
                images = tweet.find_elements(By.XPATH, './/img[contains(@src, "twimg.com/media")]')
                image_urls = [img.get_attribute("src") for img in images]

                # get timestamp
                try:
                    timestamp = tweet.find_element(By.XPATH, './/time').get_attribute("datetime")
                except:
                    timestamp = "Unknown"

                tweet_data = {
                    "text": text,
                    "images": image_urls,
                    "timestamp": timestamp,
                    "tweet_id": tweet_id
                }
                print(f"Collected tweet {tweet_id}")

                liked_tweets.append(tweet_data)
                collected_tweet_ids.append(tweet_id)

            # scroll down to load more tweets
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            scroll_attempts += 1

        if(collected_tweet_ids):
            # save last post id
            self.last_post_id = collected_tweet_ids[0]

        print(f"Collected {len(liked_tweets)} liked tweets.")

        self._save_likes(liked_tweets)

    def _save_likes(self, liked_tweets):
        for tweet in liked_tweets:
            text = tweet["text"]
            images = tweet["images"]
            timestamp = tweet["timestamp"]

            print("\n📌 推文内容:", text)
            if images:
                print("🖼️ 图片:", images)
            print("🕒 时间戳:", timestamp)
            print("-" * 50)
        pass


