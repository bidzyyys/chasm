Scenario: Key generation
Given Datadir: datadir, password: test1234test1234

When Datadir does not exist
And Alice creates new account

Then Datadir exists
And Keys are valid
And Cleanup is done
