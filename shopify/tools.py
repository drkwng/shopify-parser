import csv
from itertools import product, zip_longest


def get_proxies(filename):
    """
    Read proxy file (1 proxy per line)
    USER:PASSWORD@IP:PORT
    """
    with open(filename, 'r', encoding='utf-8') as file:
        proxies = [line.strip() for line in file]
    return proxies


def get_search_query():
    """
    Generate all possible 5 letter suggestions
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for r in range(1, 6):
        for query in product(alphabet, repeat=r):
            yield ''.join(query)


def query_proxy_combo(queries, proxy_file):
    """
    Create combitations of queries and proxies
    """
    # queries = [query for query in get_search_query()]
    proxies = get_proxies(proxy_file)
    proxies_count = len(queries) // (len(proxies) + 1)

    for combo in zip_longest(queries, proxies * proxies_count):
        yield combo


def csv_writer(res_file, mode, data):
    """
    Write data into a CSV
    """
    with open(res_file, mode, encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        if mode == 'w':
            writer.writerow(data)
        else:
            for el in data:
                writer.writerow([
                    el['query'], el['letters_cnt'], el['position'], el['suggestion'],
                    el['page_type'], el['results_count']
                ])


def get_queries(filename):
    """
    Read queries from file
    """
    with open(filename, 'r', encoding='utf-8') as file:
        queries = [line.strip() for line in file]
    return queries


if __name__ == "__main__":
    for i in get_search_query():
        print(i)
