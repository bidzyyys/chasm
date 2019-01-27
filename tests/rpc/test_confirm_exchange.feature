Scenario: Exchange confirmation
Given Alice has 100 bdzys in 1 UTXO and Bob has 50 bdzys in 1 UTXO

When Alice creates exchange offer: 1 btc for 10 xpc
And Bob accepts the offer
And Carol confirms the exchange

Then Confirmation exists
And There is 0 offer matched by Bob
And Alice has 0 accepted offer