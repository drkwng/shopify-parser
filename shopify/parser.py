import os
import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from fake_useragent.fake import UserAgent


class Driver:
    def __init__(self, proxy):
        self.proxy = proxy
        self.ua = {'user-agent': UserAgent().chrome}

    def start_driver(self):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Maximized window (headless mode fix)
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        options.add_argument(f"user-agent={self.ua}")
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')

        options.add_argument("--profile-directory=Default")
        # options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

        driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=options
        )

        return driver


class ShopifyParser(Driver):
    def __init__(self, proxy=''):
        super().__init__(proxy)
        os.environ["WDM_LOG_LEVEL"] = "0"

        self.driver = self.start_driver()
        self.driver.switch_to.new_window('tab')

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
            return 'collection'
        elif '/categories/' in url:
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

    def check_suggestion(self, url, query, num):
        """
        Open new tab. Input a query and click on certain suggestion (num) and scrape data
        """
        self.driver.switch_to.new_window('tab')
        self.driver.get(url)
        # Find input
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
        if page_type == 'search' or page_type == 'collection':
            results_count = self.get_results_amount(
                self.driver.find_element(By.XPATH, self.search_results_xpath).text
            )

        # Close current tab and switch to the first opened tab
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[1])

        return {
            'page_type': page_type,
            'results_count': results_count
        }

    def worker(self, query):
        """
        First open page https://apps.shopify.com/ (start_url) to scrape all the suggestions by query.
        After that open start_url as many times as there are suggestions amount.
        Click on each suggestion, load and classify page, scrape search results amount.
        """
        # First iteration to get all suggestions
        start_url = 'https://apps.shopify.com/'
        self.driver.get(start_url)

        input_element = self.driver.find_element(
            By.XPATH,
            self.search_input_xpath
        )
        input_element.click()
        # timeout to render suggestion overflow
        sleep(1)
        input_element.send_keys(query)
        sleep(1)

        # Scrape all the suggestions without clicking
        suggestions_elements = self.driver.find_elements(
            By.XPATH,
            self.search_suggestions_xpath
        )
        suggestions_text = [elem.text for elem in suggestions_elements]

        final_data = []
        if len(suggestions_text) > 1:
            for num in range(len(suggestions_text)):
                result = self.check_suggestion(start_url, query, num)

                final_data += [{
                    'query': query,
                    'position': num + 1,
                    'suggestion': suggestions_text[num],
                    'page_type': result['page_type'],
                    'results_count': result['results_count']
                }]

        else:
            result = self.check_suggestion(start_url, query, 0)
            final_data += [{
                'query': query,
                'position': 1,
                'suggestion': suggestions_text[0],
                'page_type': result['page_type'],
                'results_count': result['results_count']
            }]

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.switch_to.new_window('tab')
        return final_data


if __name__ == "__main__":
    keyword = input('Please type the search query: ').strip()
    parser = ShopifyParser()
    print(parser.worker(keyword))
