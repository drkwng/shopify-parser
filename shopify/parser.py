import os
import gc
import re
import threading

import csv
from time import sleep

from multiprocessing.pool import ThreadPool
from selenium.webdriver.common.by import By

from driver import Driver
from tools import csv_writer


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
    sleep(1)
    input_element.send_keys(query)
    sleep(1)

    driver.find_elements(
        By.XPATH,
        search_suggestions_xpath
    )[num].click()

    page_type = classify_page(driver.current_url)

    # Get results count for Search results pages and Category pages
    results_count = ''
    if page_type == 'search' or page_type == 'collection':
        results_count = get_results_amount(
            driver.find_element(
                By.XPATH,
                search_results_xpath
            ).text
        )

    # Close current tab and switch to the first opened tab
    driver.close()
    driver.switch_to.window(driver.window_handles[1])

    return {
        'page_type': page_type,
        'results_count': results_count
    }


def worker(query):
    """
    First open page https://apps.shopify.com/ (start_url) to scrape all the suggestions by query.
    After that open start_url as many times as there are suggestions amount.
    Click on each suggestion, load and classify page, scrape search results amount.
    """
    print(f'Start sraping query: {query}')
    driver = Driver.create_driver()

    # First iteration to get all suggestions
    start_url = 'https://apps.shopify.com/'
    driver.get(start_url)

    input_element = driver.find_element(
        By.XPATH,
        search_input_xpath
    )
    input_element.click()
    # timeout to render suggestion overflow
    sleep(0.5)
    input_element.send_keys(query)
    sleep(1)

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
                'position': num + 1,
                'suggestion': suggestions_text[num],
                'page_type': result['page_type'],
                'results_count': result['results_count']
            }]

    else:
        result = check_suggestion(driver, start_url, query, 0)
        final_data += [{
            'query': query,
            'position': 1,
            'suggestion': suggestions_text[0],
            'page_type': result['page_type'],
            'results_count': result['results_count']
        }]

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    # driver.switch_to.new_window('tab')

    csv_writer('results/results.csv', 'a', final_data)


if __name__ == "__main__":
    threadLocal = threading.local()

    # keyword = input('Please type the search query: ').strip()
    keywords = ['appl', 'paym', 'dsf']
    proxy = ''

    proxies = [

    ]

    number_of_processes = min(8, len(proxies))
    with ThreadPool(processes=number_of_processes) as pool:
        result_array = pool.map(worker, keywords)
        # Must ensure drivers are quitted before threads are destroyed:
        del threadLocal
        # This should ensure that the __del__ method is run on class Driver:
        gc.collect()
        pool.close()
        pool.join()

