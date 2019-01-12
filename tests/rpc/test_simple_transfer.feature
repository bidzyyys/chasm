Scenario: Alice sends to Bob some money
Given Alice has 100 bdzys in 1 UTXO and Bob has 0 bdzys in 0 UTXO

When Alice sends 10 bdzys to Bob with 1 bdzys transaction fee

Then Alice has 89 bdzys
And Bob has 10 bdzys
And Transaction exists