Scenario: Display keys
Given Password for all keys: test1234test1234

When Alice creates 2 new accounts

Then Keystore exists
And 2 accounts exist