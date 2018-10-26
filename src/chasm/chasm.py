"""Simple ABCI for peercoin.
"""


def foo(some_bool):
    if some_bool:
        return 1
    else:
        return 2


def cli():
    """Main method"""
    foo(False)


if __name__ == "__main__":
    cli()
