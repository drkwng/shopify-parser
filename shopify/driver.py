import os
import threading

from fake_useragent.fake import UserAgent
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

threadLocal = threading.local()


class Driver:
    def __init__(self, _proxy=''):
        os.environ["WDM_LOG_LEVEL"] = "0"

        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--profile-directory=Default")
        # options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

        # Maximized window (headless mode fix)
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        ua = {'user-agent': UserAgent().chrome}
        options.add_argument(f"user-agent={ua}")

        if _proxy:
            options_seleniumwire = {
                'proxy': {
                    'https': f'https://{_proxy}',
                }
            }
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=options,
                seleniumwire_options=options_seleniumwire
            )
        else:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=options
            )

        # self.driver.switch_to.new_window('tab')

    def __del__(self):
        self.driver.quit()

    @classmethod
    def create_driver(cls, _proxy=''):
        the_driver = getattr(threadLocal, 'the_driver', None)
        if the_driver is None:
            the_driver = cls(_proxy)
            threadLocal.the_driver = the_driver
        driver = the_driver.driver
        the_driver = None
        return driver
