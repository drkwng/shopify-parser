import re

from time import sleep

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .driver import Driver
from .tools import csv_writer


# XPATH Expressions
search_input_xpath = '//form[@id="UiSearchInputForm"]/*/*/input[@type="search"]'
search_suggestions_xpath = '//li[@class="ui-search-suggestions__suggestions-item "]'


def get_suggestion_type(element):
    try:
        image = element.find_element(by=By.TAG_NAME, value="img").get_attribute("src")
        if '/app-store/' in image:
            return 'app'
        else:
            return 'search'
    except NoSuchElementException:
        return 'category'


def worker(query):
    """
    First open page https://apps.shopify.com/ (start_url) to scrape all the suggestions by query.
    After that open start_url as many times as there are suggestions amount.
    Click on each suggestion, load and classify page, scrape search results amount.
    """
    if len(query) > 0:
        print(f'Start sraping query: {query}\n')
        driver = Driver.create_driver()
        driver.switch_to.new_window('tab')
        start_url = 'https://apps.shopify.com/'
        driver.get(start_url)

        input_element = driver.find_element(
            By.XPATH,
            search_input_xpath
        )
        input_element.click()
        # timeout to render suggestion overflow
        sleep(1)
        input_element.send_keys(query)
        sleep(1)

        # Scrape all the suggestions without clicking
        suggestions_elements = driver.find_elements(
            By.XPATH,
            search_suggestions_xpath
        )

        final_data = []
        for num, elem in enumerate(suggestions_elements, start=1):
            suggestion_type = get_suggestion_type(elem)
            result = {
                'query': query,
                'letters_cnt': len(query),
                'position': num,
                'suggestion': elem.text,
                'page_type': suggestion_type
            }
            final_data += [result]

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        csv_writer('results/results.csv', 'a', final_data)
