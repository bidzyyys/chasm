Scenario: Sign given transaction
Given New datadir: datadir, new address and hash of the transaction

When I sign the transaction

Then Signature is valid
And Datadir is removed