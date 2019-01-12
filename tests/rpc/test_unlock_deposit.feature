Scenario: Alice unlocks deposit
Given Alice has 100 bdzys in 1 UTXO

When Alice creates an exchange offer
And Alice creates UnlockDeposit transaction, deposit 12, transaction fee 1

Then UnlockDeposit transaction exists