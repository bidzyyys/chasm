# chasm

[![Build Status](http://jenkins.xpeer.network/buildStatus/icon?job=chasm/master)](http://jenkins.xpeer.network/job/chasm/job/master/)
[![Code Coverage](http://jenkins.xpeer.network:5000/coverage/chasm/job/master)](http://jenkins.xpeer.network:5000/coverage/chasm/job/master)

# Overview

Bachelor's Thesis PoC

## Installation

The following packages must be installed:
```
leveldb
boost 1.68.0
```

## Protocol

xpeer's protocol enables users to make both simple transfers and exchanges of multiple cryptocurrencies. Each vital information is stored on a blockchain.
Blocks are mined every minute and their size is limited to 1MB. With such frequency blocks can be empty too. Having explored a block, miners are awarded with
extra sum of money(that totals to fees and minted coins), what makes it easy to get xpeer(not only through an exchange at cryptomarket).

xpeer's transactions are quite similar to Bitcoin's - they take inputs and produce [UTXOs](https://www.mycryptopedia.com/bitcoin-utxo-unspent-transaction-output-set-explained/).
UTXO contains parameters necessary for a validation process. It is more complicated than in Bitcoin, but it arises from an exchange feature.

#### Simple transfer

To make a simple transfer user has to specify the amount of money to be sent, the receiver's address and the amount of money to be sent back. Our protocol enables only to send 
all the owner's funds, so the only one solution is to transfer the rest of money to oneself. There is no restriction related to receivers' quantity.
Transfer is getting valid when is included into xpeer's blockchain. To make it faster user should leave higher mining fee. Of course,
there is an award for miners when they find a block, but it is slowly decreasing and one day will have become 0. Miners are not obligated to explore blocks,
so without any incentive there is a small possibility to get the transaction involved. Mining consumes a lot of electricity, so it should be obvious that miners
do not want to have losses.


#### Making an offer

Making an offer is a first step of an exchange. Our protocol treats offers as simple transfers, but they contain more information.
Maker has to specify which currency is being sold and the value, which currency is expected and also value. What is more, user has to provide an address for a payment.
It is widely known that each currency has a specific addresses' length, usually different through the range of crypto, so it is also automatically included.
Another important factor are fees (in xpeer currency) - for adding an offer, for confirmation of the offer and the deposit in case of cheating. Offers have more data to process
than simple transfers, so miners have more expensive computations. This is the way to make the offer valid in a blockchain faster - the more mining fee,
the more miners who want to catch it. It is worth mentioning that the offer becomes visible only when is included in xpeer's blockchain. The same with incentive for adding
a confirmation block, which requires the most computations in our protocol. A deposit is a kind of protection for cheating. When the side of exchange plays the game, it is handed back. 
There is also another vital information - timeout. Timeout says how much time an offer is valid and, in case of acceptance, how much time sides have for an exchange then.


#### Taking an offer

Taking an offer means that one find an offer and is willing to exchange its money. That info makes some kind of a contract between those two sides, each of them agrees to
send funds on time. In our protocol it means that an acceptance transaction is involved into xpeer's blockchain. In addition to inputs and outputs lists, acceptance transaction
contains hash of the offer, specifies taker's address for income and can be created only if matching offer exists in our blockchain. To make an acceptance, user has to send fees
that are the same as in an offer.


#### Transaction's confirmation

Transaction's confirmation is kind of information that both sides of a trade have sent money that they had agreed before. This is necessary for unlocking funds included
in the exchange (each currency will have a mechanism that checks xpeer's blockchain for confirmations when the trade is done) and for getting back the deposit.
Confirmations contain only inputs and outpus and hash of the offer, but requires the most calculations. They are automatically added when an exchange is finished,
but not only depends it on our blockchain but also requires validation of other cryptocurrencies' transactions.
 

#### Unlocking deposit

When at least one side of exchange does not honor an obligation of sending funds, confirmation is not added into xpeer's blockchain. It means that sides cannot get the
deposit back. The honest one can make an order that verifies its innocence. The order is nothing but verification of sent currency's blockchain to prove that funds
has been sent. Then the result of that research is added into xpeer's blockchain. This kind of commission requires transaction fee and additionally another __deposit__.
That deposit is the same as the one that user want to get back. It is connected with minimization of possible jobs that may overload our network. Unlocking can be done when 
the time for an exchange is out.

In case of unaccepted offer, the way of getting money back is quite similar. Maker has to specify hash of the offer and pay transaction fee and a __deposit__. If there is no 
offer acceptance the deposit and the fee for a confirmation block is unlocked, in other case those deposits and fees are finally blocked. 

Both results are included into xpeer's blockchain as a kind of transaction. 


### UTXO
   There are two types of transactions' outputs distinguished by the first param:
   
   __1) Simple transfer to address given as a second param.__
   
   To unlock it, one have to provide its signature(private key) compatible with public key
   given in previous output.

   __2) Part of an exchange.__ 
   
   Here one has to specify hash of the offer and possible receiver's address and timestamp with address of
   possible return. To unlock that funds there must be a confirmation block of that offer and given receiver's signature or time is out and previous owner's signature. 
   There is a possibility when both sides can unlock that funds - time is over and exchange was confirmed. The current owner has to remember to transfer its money another
    one on time, if not, the previous one can spend it. It eliminates amount of money which is unused.

##### We as authors inform each user about that possibility and are not responsible for those deceits.

As an __input__ one provides hash of the block with previous transaction, position of the transaction in a block and its signing key.

Then outputs and inputs are verified in an enclave and as a result funds are unlocked or not.    

## Protocol's assumptions
   __1) Transaction's restriction__
   Besides minting, sum of transactions' inputs cannot be greater than sum of transaction's outputs. It should be obvious that users cannot
   produce money.
   
   <p align="center">
        <img src="/docs/images/in_out.gif" />
   </p>
   
   __2) Award for mining a block__
   
   Each block as a first transaction has minting - newly created amount of money which belongs to the miner. That amount starts from ``` ``` and __every 2 years__ is
   divided by 2. It is a kind of encouragement for people to start mining.
   
   It is presented as a Minting transaction - first transaction in every block that has no inputs.

   __3) Mining fee__
   
   Mining fee is another award for mining blocks. Higher fees are catchy for miners, so those transactions are faster included in blocks. 
   Mining fee is a difference between inputs and outputs: 
   
   <p align="center">
       <img src="/docs/images/sum.gif" />
   </p>
   	
   __4) Deposit's amount__
   
   The deposit's fee has to be __at least 10 times larger__ than a transaction's fee in a block. It is a protocols requirement protecting from cheating and DDoS attack 
   on xpeer's network(steady requests to unlock deposit). Transactions which do not meet this requirement are included in a blockchain, but are not valid and cannot be spent.
   
## Data structures 

   __1) Block__
   <p align="center">
        <img src="/docs/images/block.png" alt="Image" />
   </p>

   Blocks' size is limited to 1MB. In xpeer's blockchain data is stored as a binary format to minimize amount of unnecessary information,
   each attribute has specified number of bytes and its position. There is also a strict convention how to serialize data with various length, e.g. other cryptocurrencies'
   wallet addresses.

   __Header__ - contains information about block

   <p align="center">
        <img src="/docs/images/header.png" alt="Image" />
   </p>

   __List of various transactions__

   <p align="center">
        <img src="/docs/images/transactions.png" alt="Image" />
   </p>


<p align="center">
    <img src="/docs/images/in_out.png" alt="Image" />
</p>


<p align="center">
    <img src="/docs/images/offer.png" alt="Image" />
</p>


<p align="center">
    <img src="/docs/images/minting.png" alt="Image" />
</p>


<p align="center">
    <img src="/docs/images/acceptance.png" alt="Image" />
</p>


<p align="center">
    <img src="/docs/images/confirmation.png" alt="Image" />
</p>


<p align="center">
    <img src="/docs/images/unlocking.png" alt="Image" />
</p>



## System architecture




    
