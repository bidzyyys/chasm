extern crate chasm;

use chasm::primitives::transaction::*;

#[test]
fn sample_test(){
    let t = build_transaction(10);

    assert_eq!(t.tx_hash, Transaction{tx_hash: 10}.tx_hash);
}