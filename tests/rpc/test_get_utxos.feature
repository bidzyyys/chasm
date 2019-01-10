Scenario: Get UTXOs of non-existing address
Given Address: aaaa

When I get UTXOs
And I count balance of the account

Then UTXOs sum to balance
And Address has 0 bdzys in 0 UTXOs

Scenario: Get UTXOs of existing address
Given Address: 3056301006072a8648ce3d020106052b8104000a0342000405b4cf876a3925864057c44579af1698a9c5c1610304f6738f6b48f2399f8c448394a33d80a34f54e93b818438710cb25e983e49fc6d916babd4b25c55cc9b14

When Initialized address has 100 bdzys in 2 UTXOs
And I get UTXOs
And I count balance of the account

Then UTXOs sum to balance
And Address has 100 bdzys in 2 UTXOs