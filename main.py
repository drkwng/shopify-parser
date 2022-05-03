from multiprocessing.pool import ThreadPool, Pool

from shopify.tools import csv_writer, get_search_query
from shopify.parser import ShopifyParser


def main():
    res_file = 'results/results.csv'
    heading = ['QUERY', 'POSITION', 'SUGGESTION', 'PAGE_TYPE', 'RESULTS_COUNT']
    csv_writer(res_file, 'w', heading)

    parser = ShopifyParser()
    for i in get_search_query():
        print('Program has started. Stay calm and wait for the end...')
        try:
            result = parser.worker(i)
            csv_writer(res_file, 'a', result)
            print(f'{i} Done!')

        except Exception as err:
            print(err, type(err))

    print(f'Done. Check the result in  "{res_file}"')


if __name__ == "__main__":
    main()
