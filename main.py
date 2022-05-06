import gc
import threading
from multiprocessing.pool import ThreadPool

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
    thread_local = threading.local()

    results_file = 'results/results.csv'
    proxies_file = 'proxies.txt'
    heading = ['QUERY', 'LETTERS_COUNT', 'POSITION', 'SUGGESTION', 'PAGE_TYPE', 'RESULTS_COUNT']
    csv_writer(results_file, 'w', heading)

    mode = choose_mode()
    if mode == '1':
        queries = [query for query in get_search_query()]
        print(f'You chose "Scrape by generated suggestions (approx. 12M queries)"\n')
    else:
        queries = get_queries('queries.txt')
        print(f'You chose "Scrape by list of suggestions" ({len(queries)} queries)\n')

    number_of_processes = min(10, len(get_proxies('proxies.txt')))
    with ThreadPool(processes=number_of_processes) as pool:
        pool.starmap(worker, query_proxy_combo(queries, proxies_file))
        # Must ensure drivers are quited before threads are destroyed:
        del thread_local
        # This should ensure that the __del__ method is run on class Driver:
        gc.collect()
        pool.close()
        pool.join()

    print(f'Done! Check the "{results_file}" in the program folder.')


if __name__ == "__main__":
    main()
