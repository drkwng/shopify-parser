import itertools


def get_search_query():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for r in range(1, 6):
        for query in itertools.product(alphabet, repeat=r):
            yield ''.join(query)


if __name__ == "__main__":
    for i in get_search_query():
        print(i)
