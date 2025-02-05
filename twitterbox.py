from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import localstorage

MAX_RECENT_LIKES = 500  # local storage max likes

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
        self.current_refresh_interval = self.refresh_interval
        self.filter_tags = config['bot']['filter_tags']
        self.trigger = config['bot']['trigger']
        self.save_path = config['bot']['save_path']

        self.saved_posts_id = localstorage.load_recent_ids(MAX_RECENT_LIKES)

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
        
        if self.user_agent:
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
                collected_posts, collected_ids = self._get_posts(self.max_post_num)
                self._save_posts(collected_posts, collected_ids)
                self._smart_sleep(collected_posts)

        except Exception as e:
            print('Bot stopped running. Error occured:',e)
            self.driver.quit()
            return
    
    def refresh(self):
        driver = self.driver
        driver.refresh()

    def clear_cache(self):
        self.saved_posts_id.clear()
        localstorage.save_recent_ids(self.saved_posts_id)

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

    def _get_posts(self, max_post_num):
        driver = self.driver
        TWITTER_USERNAME = self.username

        print("Fetching tweets...")

        # get posts URL
        if self.trigger == "like":
            posts_url = f"https://twitter.com/{TWITTER_USERNAME}/likes"
        elif self.trigger == "bookmark":
            posts_url = "https://twitter.com/i/bookmarks"
        else:
            raise Exception("Unsupported trigger")
        
        driver.get(posts_url)
        time.sleep(5)

        collected_tweets = []
        collected_tweet_ids = []
        scroll_attempts = 0
        max_scrolls = 100 
        get_new = True

        while get_new and len(collected_tweets) < max_post_num and scroll_attempts < max_scrolls:
            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            get_new = False
            for tweet in tweets:
                
                # get tweet id
                tweet_link = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]').get_attribute("href")
                tweet_id = tweet_link.split("/")[-1] 
                print(f"Checking tweet {tweet_id}")

                if tweet_id in self.saved_posts_id:
                    scroll_attempts = max_scrolls
                    break
                if tweet_id in collected_tweet_ids:
                    continue 
                get_new = True

                # get text content
                try:
                    text = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                except:
                    text = ""

                # filter by tags
                print(f"Filter tags: {self.filter_tags}")
                print(f"Tweet text: {text}")
                if self.filter_tags:
                    if not any(tag in text for tag in self.filter_tags):
                        continue
                
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

                collected_tweets.append(tweet_data)
                collected_tweet_ids.append(tweet_id)

            # scroll down to load more tweets
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            scroll_attempts += 1

        self._log(collected_tweets)

        return collected_tweets, collected_tweet_ids

    def _save_posts(self, collected_posts, collected_ids):
        # update recent likes
        for id in collected_ids[::-1]:
            self.saved_posts_id.append(id)
        while len(self.saved_posts_id) > MAX_RECENT_LIKES:
            self.saved_posts_id.popleft()

        # save recent likes
        localstorage.save_recent_ids(self.saved_posts_id) 

        # save posts
        localstorage.save_posts(collected_posts, self.save_path)
        
    def _smart_sleep(self, get_new):
        if get_new:
            self.current_refresh_interval = max(self.refresh_interval * 0.2, self.current_refresh_interval // 2)
        else:
            self.current_refresh_interval = min(self.current_refresh_interval * 2, self.refresh_interval * 2)
        print(f"Sleeping for {self.current_refresh_interval} seconds...")
        time.sleep(self.current_refresh_interval)

    def _log(self, collected_tweets):
        print(f"Collected {len(collected_tweets)} liked tweets.")
        for tweet in collected_tweets:
            text = tweet["text"]
            images = tweet["images"]
            timestamp = tweet["timestamp"]

            print("\n📌 推文内容:", text)
            if images:
                print("🖼️ 图片:", images)
            print("🕒 时间戳:", timestamp)
            print("-" * 50)
        pass


