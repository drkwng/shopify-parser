import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

from fake_useragent.fake import UserAgent

from time import sleep


class ShopifyParser:
    def __init__(self):
        os.environ["WDM_LOG_LEVEL"] = "0"

        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.ua = {'user-agent': UserAgent().chrome}
        options.add_argument(f"user-agent={self.ua}")

        options.add_argument("--profile-directory=Default")
        options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=options
        )

    @staticmethod
    def classify_page(url):
        if '/search' in url:
            return 'search'
        elif '/collections/' in url:
            return 'category'
        else:
            return 'app'

    def scrape_suggestions(self):
        pass

    def worker(self, query):
        start_url = 'https://apps.shopify.com/'
        self.driver.get(start_url)
        self.driver.maximize_window()

        input_element = self.driver.find_element(
            By.XPATH,
            '//form[@id="UiSearchInputForm"]/*/*/input[@type="search"]'
        )
        input_element.click()
        sleep(1)
        input_element.send_keys(query)
        sleep(1)

        suggestions_elements = self.driver.find_elements(
            By.XPATH,
            '//li[@class="ui-search-suggestions__suggestions-item "]'
        )
        suggestions_text = [elem.text for elem in suggestions_elements]

        if len(suggestions_text) > 1:
            for num in range(len(suggestions_text)):
                self.driver.switch_to.new_window('tab')
                self.driver.get(start_url)

                input_element = self.driver.find_element(
                    By.XPATH,
                    '//form[@id="UiSearchInputForm"]/*/*/input[@type="search"]'
                )
                input_element.click()
                sleep(1)
                input_element.send_keys(query)
                sleep(1)
                self.driver.find_elements(
                    By.XPATH,
                    '//li[@class="ui-search-suggestions__suggestions-item "]'
                )[num].click()

                print(num + 1, suggestions_text[num], self.classify_page(self.driver.current_url))

                # TODO: Make a page crawler as separate function
                # TODO: Open several tabs
                # TODO: Close existing tabs
                # TODO: Scrape other data if it is search results type
        else:
            suggestions_elements[0].click()

            print(1, query, self.classify_page(self.driver.current_url))

        self.driver.close()
        self.driver.quit()


if __name__ == "__main__":
    parser = ShopifyParser()
    parser.worker('app')
