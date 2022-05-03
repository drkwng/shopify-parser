import itertools
import csv


def get_search_query():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for r in range(1, 6):
        for query in itertools.product(alphabet, repeat=r):
            yield ''.join(query)


def csv_writer(res_file, mode, data):
    with open(res_file, mode, encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        if mode == 'w':
            writer.writerow(data)
        else:
            for el in data:
                writer.writerow([
                    el['query'], el['position'], el['suggestion'],
                    el['page_type'], el['results_count']
                ])


if __name__ == "__main__":
    for i in get_search_query():
        print(i)

    # print([i for i in get_search_query()])
