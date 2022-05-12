from shopify.driver import Driver
from shopify.parser import worker
from shopify.tools import *


def choose_mode():
    while True:
        mode = input('Please choose mode (type digit only): \n'
                     '1 - Scrape by generated suggestions (approx. 12M queries)\n'
                     '2 - Scrape by list of suggestions\n')
        if mode == '1':
            return '1'
        elif mode == '2':
            return '2'
        else:
            print('Please print the correct mode digit (1 or 2)')


def main():
    results_file = 'results/results.csv'
    heading = ['QUERY', 'LETTERS_COUNT', 'POSITION', 'SUGGESTION', 'PAGE_TYPE']
    csv_writer(results_file, 'w', heading)

    mode = choose_mode()
    if mode == '1':
        queries = [query for query in get_search_query()]
        print(f'You chose "Scrape by generated suggestions (approx. 12M queries)"\n')
    else:
        queries = get_queries('queries.txt')
        print(f'You chose "Scrape by list of suggestions" ({len(queries)} queries)\n')

    driver = Driver.create_driver()
    start_url = 'https://apps.shopify.com/'
    driver.get(start_url)

    for query in queries:
        worker(driver, query)

    print(f'Done! Check the "{results_file}" in the program folder.')
    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()
