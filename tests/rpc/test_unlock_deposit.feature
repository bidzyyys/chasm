Scenario: Alice unlocks deposit
Given Alice has 100 bdzys in 1 UTXO

When Alice creates exchange offer: 1 btc for 10 xpc, receive aaaa, deposit: 10, transaction fee: 1 confirmation fee: 2
And Alice creates UnlockDeposit transaction, deposit 10, transaction fee 1

Then UnlockDeposit transaction exists
And Alice has 74 bdzys
And Cleanup is done