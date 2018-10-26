# def test_bytes_signed_by_alice_can_be_verified(alice):
#     (priv_key, pub_key) = alice
#     random_bytes = b'lorem impsum'
#     signature = priv_key.sign(random_bytes)
#     assert pub_key.verify(signature, random_bytes)


class AClass:
    class_counter = 0

    def __init__(self):
        self.counter = 0
        AClass.class_counter += 1


def test_playground():
    q = AClass()
    w = AClass()

    q.class_counter = 10
    e = AClass()
    AClass.class_counter = 12
    print(e)