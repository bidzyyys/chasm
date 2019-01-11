Scenario: Bob matches offer
Given Alice has 100 bdzys in 1 UTXO and Bob has 100 bdzys in 1 UTXO

When Alice creates exchange offer: 1 btc for 10 xpc, receive aaaa
And Bob accepts it deposit: 12, confirmation fee: 2, transaction fee: 1, receive bbbb

Then Offer match exists
And Bob has 85 xpc
And There is 1 accepted offer by Alice
And There is 1 offer match by Bob
And There is no accepted offer with fake address
And There is no offer match with fake address