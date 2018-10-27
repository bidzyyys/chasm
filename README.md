# chasm

[![Build Status](http://jenkins.xpeer.network/buildStatus/icon?job=chasm/master)](http://jenkins.xpeer.network/job/chasm/job/master/)
[![Code Coverage](http://jenkins.xpeer.network:5000/coverage/chasm/job/master)](http://jenkins.xpeer.network:5000/coverage/chasm/job/master)

# Overview

Bachelor's Thesis PoC

## Installation

The following packages must be installed:
```
leveldb
```

## Protocol
![block](docs/images/block.png)

![header](docs/images/header.png)

![transactions](docs/images/transactions.png)



  
#### Simple transfer
![transaction](docs/images/transaction.png)

xpeer's transactions are quite similar to [Bitcoin's UTXO](https://www.mycryptopedia.com/bitcoin-utxo-unspent-transaction-output-set-explained/).
That amount of money comes from usually multiple inputs and is sent to at least one address. It is clear when one send all funds into another address,
but when somebody want to spend only a part of it, the rest is sent back to the owner's address. There must be a mining fee to encourages miners to 
include that transaction in a block. The mining fee is a difference between inputs and outputs and is not defined directly, one must remember to make some part of that funds left.
```Maining fee = Input 0..N - Output 0..N```

#### Making an offer
![offer](docs/images/offer.png)

#### Offer acceptance
![acceptance](docs/images/acceptance.png)

#### Transaction confirmation
![confirmation](docs/images/confirmation.png)

#### Unlocking deposit
![unlocking](docs/images/unlocking.png)

#### Way of using funds
![in_out](docs/images/in_out.png)


## System architecture