import yaml
from twitterbox import TwitterBox

if __name__ == "__main__":
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    bot = TwitterBox(config)
    bot.run()
