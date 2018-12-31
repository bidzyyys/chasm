Scenario: Valid simple transaction
Given Alice has 10 xpc and Bob has 0 xpc

When Alice transfers 2 xpc to Bob and pays 0.1 xpc tx_fee

Then Alice gets an acceptance
And Now Bob has 2 xpc and Alice has 7.9 xpc

Scenario: Invalid simple transaction
Given Eve has 10 xpc and Alice has 0 xpc

When Eve transfers 15 xpc to Alice and pays 0.1 xpc tx_fee

Then Eve gets an error
And Now Eve has 10 xpc and Alice has 0.0 xpc