import os

import re

from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

from fake_useragent.fake import UserAgent


class ShopifyParser:
    def __init__(self):
        os.environ["WDM_LOG_LEVEL"] = "0"

        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # TODO: Implement Headless mode
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

        # XPATH Expressions
        self.search_input_xpath = '//form[@id="UiSearchInputForm"]/*/*/input[@type="search"]'
        self.search_suggestions_xpath = '//li[@class="ui-search-suggestions__suggestions-item "]'
        self.search_results_xpath = '//div[@class="grid__item grid__item--tablet-up-half grid__item--wide-up-third"]'

    @staticmethod
    def classify_page(url):
        """
        Classify if page is search results, category or an app page
        """
        if '/search' in url:
            return 'search'
        elif '/collections/' in url:
            return 'category'
        else:
            return 'app'

    @staticmethod
    def get_results_amount(data):
        """
        Get search results amount from scraped string
        """
        try:
            result = re.sub(
                r'(.*[0-9]*[0-9] of)? ([0-9].*[0-9]) results', r'\2',
                data
            ).split(' ')[0]
        except re.error:
            result = 'N/A'
        return result

    def check_suggestion(self, num, query):
        """
        Type in a query and click on certain suggestion
        """
        input_element = self.driver.find_element(
            By.XPATH,
            self.search_input_xpath
        )
        input_element.click()
        # timeout to render suggestion overflow
        sleep(1)
        input_element.send_keys(query)
        sleep(1)
        self.driver.find_elements(
            By.XPATH,
            self.search_suggestions_xpath
        )[num].click()

        page_type = self.classify_page(self.driver.current_url)

        # Get results count for Search results pages and Category pages
        results_count = ''
        if page_type != 'app':
            results_count = self.get_results_amount(
                self.driver.find_element(By.XPATH, self.search_results_xpath).text
            )

        return {
            'page_type': page_type,
            'results_count': results_count
        }

    def worker(self, query):
        # First iteration to get all suggestions
        start_url = 'https://apps.shopify.com/'
        self.driver.get(start_url)
        self.driver.maximize_window()

        input_element = self.driver.find_element(
            By.XPATH,
            '//form[@id="UiSearchInputForm"]/*/*/input[@type="search"]'
        )
        input_element.click()
        # timeout to render suggestion overflow
        sleep(1)
        input_element.send_keys(query)
        sleep(1)

        # Scrape all the suggestions without clicking
        suggestions_elements = self.driver.find_elements(
            By.XPATH,
            '//li[@class="ui-search-suggestions__suggestions-item "]'
        )
        suggestions_text = [elem.text for elem in suggestions_elements]

        if len(suggestions_text) > 1:
            for num in range(len(suggestions_text)):
                self.driver.switch_to.new_window('tab')
                self.driver.get(start_url)
                result = self.check_suggestion(num, query)
                print(num + 1, query, suggestions_text[num],
                      result['page_type'], result['results_count'])
                # TODO: Store results data except of print calling
                # TODO: Close tabs after finish scraping
        else:
            suggestions_elements[0].click()
            print(1, query, suggestions_text[0], self.classify_page(self.driver.current_url))

        self.driver.close()
        self.driver.quit()


if __name__ == "__main__":
    parser = ShopifyParser()
    parser.worker('app')
