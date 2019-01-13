from chasm.consensus.validation.block_validator import BlockStatelessValidator


def test_zeroed_hash_is_always_valid():
    zeroed_hash = bytes(32)

    for i in range(256):
        assert BlockStatelessValidator.check_block_hash(zeroed_hash, i)


def test_passes_min_difficulty():
    block_hash = b'\x40' + bytes(31)

    assert BlockStatelessValidator.check_block_hash(block_hash, 1)
    assert not BlockStatelessValidator.check_block_hash(block_hash, 2)


def test_that_passes_higher_difficulty_passes_lower_as_well():
    block_hash = b'\x0f' + bytes(31)

    for i in range(4):
        assert BlockStatelessValidator.check_block_hash(block_hash, i)

    assert not BlockStatelessValidator.check_block_hash(block_hash, 5)
