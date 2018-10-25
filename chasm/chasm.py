"""Simple ABCI for peercoin.
"""


def make_sum(x_elem, y_elem):
    """Simple sum method"""
    return x_elem + y_elem


def cli():
    """Main method"""
    print(make_sum(1, 2))


if __name__ == "__main__":
    cli()
