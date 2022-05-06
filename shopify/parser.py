import re

from time import sleep

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .driver import Driver
from .tools import csv_writer


# XPATH Expressions
search_input_xpath = '//form[@id="UiSearchInputForm"]/*/*/input[@type="search"]'
search_suggestions_xpath = '//li[@class="ui-search-suggestions__suggestions-item "]'
search_results_xpath = '//div[@class="grid__item grid__item--tablet-up-half grid__item--wide-up-third"]'


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


def check_suggestion(driver, url, query, num):
    """
    Open new tab. Input a query and click on certain suggestion (num) and scrape data
    """
    driver.switch_to.new_window('tab')
    driver.get(url)
    # Find input
    input_element = driver.find_element(
        By.XPATH,
        search_input_xpath
    )
    input_element.click()
    # timeout to render suggestion overflow
    sleep(2)
    input_element.send_keys(query)
    sleep(2)
    driver.find_elements(
        By.XPATH,
        search_suggestions_xpath
    )[num].click()

    page_type = classify_page(driver.current_url)

    # Get results count for Search results pages and Category pages
    results_count = 'N/A'
    if page_type == 'search' or page_type == 'collection':
        try:
            results_count = get_results_amount(
                driver.find_element(
                    By.XPATH,
                    search_results_xpath
                ).text
            )
        except NoSuchElementException:
            results_count = '0'

    # Close current tab and switch to the first opened tab
    driver.close()
    driver.switch_to.window(driver.window_handles[1])

    return {
        'page_type': page_type,
        'results_count': results_count
    }


def worker(query, proxy):
    """
    First open page https://apps.shopify.com/ (start_url) to scrape all the suggestions by query.
    After that open start_url as many times as there are suggestions amount.
    Click on each suggestion, load and classify page, scrape search results amount.
    """
    if len(query) > 0:
        print(f'Start sraping query: {query}\n')

        driver = Driver.create_driver(proxy)

        # First iteration to get all suggestions
        start_url = 'https://apps.shopify.com/'
        driver.get(start_url)

        input_element = driver.find_element(
            By.XPATH,
            search_input_xpath
        )
        input_element.click()
        # timeout to render suggestion overflow
        sleep(2)
        input_element.send_keys(query)
        sleep(2)

        # Scrape all the suggestions without clicking
        suggestions_elements = driver.find_elements(
            By.XPATH,
            search_suggestions_xpath
        )
        suggestions_text = [elem.text for elem in suggestions_elements]

        final_data = []
        if len(suggestions_text) > 1:
            for num in range(len(suggestions_text)):
                result = check_suggestion(driver, start_url, query, num)

                final_data += [{
                    'query': query,
                    'letters_cnt': len(query),
                    'position': num + 1,
                    'suggestion': suggestions_text[num],
                    'page_type': result['page_type'],
                    'results_count': result['results_count']
                }]

        else:
            result = check_suggestion(driver, start_url, query, 0)
            final_data += [{
                'query': query,
                'letters_cnt': len(query),
                'position': 1,
                'suggestion': suggestions_text[0],
                'page_type': result['page_type'],
                'results_count': result['results_count']
            }]

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.switch_to.new_window('tab')
        csv_writer('results/results.csv', 'a', final_data)
