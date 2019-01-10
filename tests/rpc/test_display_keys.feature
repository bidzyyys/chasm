Scenario: Display keys
Given Datadir: datadir, password: test1234test1234

When Datadir exists with no keystore
And Alice creates 2 new accounts

Then Keystore exists
And 2 accounts are created
And Cleanup is done