Scenario: Alice creates exchange offer
Given Alice has 100 bdzys in 1 UTXO

When Alice creates exchange offer: 1 btc for 1000 xpc until 2019-02-01::00:00:00 confirmation fee 2 xpc transaction fee 1 xpc deposit 12 xpc with payment on her used address

Then Alice has 85 bdzys
And Offer exists
And There is 1 active offer with token: all and expected: xpc
And There is 1 active offer with token: btc and expected: xpc
And There is 1 active offer with token: btc and expected: all
And There is 0 active offer with token: eth and expected: all
And There is 0 active offer with token: all and expected: eth