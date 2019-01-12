Scenario: Key generation
Given Password: test1234test1234

When Keystore does not exist
And Alice creates new account

Then Keystore exists
And Keys are valid
