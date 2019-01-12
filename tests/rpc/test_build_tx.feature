Scenario: Build transaction from file
Given File with transaction in json format

When I build tx from file

Then I get transaction

Scenario: Failed to build transaction from invalid file
Given Invalid file with json

Then I get RuntimeError while building transaction