// Structures

extern crate sha2;

use self::sha2::Sha256;



pub struct TxInput {
//    tx_hash:
}

pub struct Transaction {
}

// Public methods
pub fn build_transaction(tx_hash: u64) -> Transaction {
    Transaction { tx_hash }
}

// Private


struct AStruct {
    aVar: u32,
    dupa: u32
}

trait Printable {
    fn print(&self) -> u32;
}

impl Printable for AStruct {
    fn print(&self) -> u32 {
        self.aVar + self.dupa
    }
}