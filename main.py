import itertools

from shopify.parser import worker
from shopify.tools import csv_writer, get_proxies, get_search_query



# def main():
#     res_file = 'results/results.csv'
#     heading = ['QUERY', 'POSITION', 'SUGGESTION', 'PAGE_TYPE', 'RESULTS_COUNT']
#     csv_writer(res_file, 'w', heading)
#
#     proxies = get_proxies('proxies.txt')
#
#     print('Program has started. Stay calm and wait for the end...')
#
#     # for i in get_search_query():
#     #     parser = ShopifyParser(proxies[0])
#     #     try:
#     #         result = parser.worker(i)
#     #         csv_writer(res_file, 'a', result)
#     #         print(f'Query "{i}" scraping done!')
#     #
#     #     except Exception as err:
#     #         print(err, type(err))
#
#     print(f'Done. Check the result in  "{res_file}"')


if __name__ == "__main__":
    pass
