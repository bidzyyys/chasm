Scenario: Alice unlocks deposit
Given Alice has 100 bdzys in 1 UTXO and Bob has 50 bdzys in 1 UTXO

When Alice creates exchange offer: 1 btc for 10 xpc
And Bob accepts the offer
And Alice creates UnlockDeposit transaction, deposit 12, transaction fee 1

Then UnlockDeposit transaction exists