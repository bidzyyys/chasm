
// Structures

pub struct Transaction{
    pub tx_hash: u64
}


// Public methods
pub fn build_transaction(tx_hash: u64) -> Transaction {
    Transaction{
        tx_hash
    }
}

// Private