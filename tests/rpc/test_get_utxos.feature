Scenario: Get UTXOs of non-existing address
Given New address

When I get UTXOs
And I count balance of the account

Then UTXOs sum to balance
And Owner has 0 bdzys in 0 UTXOs

Scenario: Get UTXOs of existing address
Given New address

When Initialized address has 100 bdzys in 2 UTXOs
And I get UTXOs
And I count balance of the account

Then UTXOs sum to balance
And Owner has 100 bdzys in 2 UTXOs