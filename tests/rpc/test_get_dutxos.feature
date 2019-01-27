Scenario: Get DUTXOs of non-existing address
Given New address

When I get DUTXOs
And I sum DUTXOs

Then Owner has 0 bdzys in 0 DUTXOs

Scenario: Get DUTXOs of existing address
Given New address

When Initialized address has 100 bdzys in 2 DUTXOs
And I get DUTXOs
And I sum DUTXOs

Then Owner has 100 bdzys in 2 DUTXOs