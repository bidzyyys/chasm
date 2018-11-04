# chasm

[![Build Status](http://jenkins.xpeer.network/buildStatus/icon?job=chasm/master)](http://jenkins.xpeer.network/job/chasm/job/master/)
[![Code Coverage](http://jenkins.xpeer.network:5000/coverage/chasm/job/master)](http://jenkins.xpeer.network:5000/coverage/chasm/job/master)

# Overview

Bachelor's Thesis PoC
The aim of the project is to implement a PoC of a DEX based on xpeer protocol.

## Installation

The following packages must be installed:
```
leveldb
boost 1.68.0
```

## Protocol
_NOTE: the following protocol is an alpha version of a protocol that may be useful when it comes to implementing a fully functional DEX. Nevertheless, it contains all parts that are required to make a swap between two different tokens ex. `Bitcoin` and `Ethereum`_ 

`xpeer` is a name of a protocol that provides trustless cross-chain exchanges. The protocol is also capable of connecting sellers with buyers.
To achieve all of above, `xpeer` protocol introduces a new intermediary blockchain. Here all the vital data is stored and it takes care of the consensus achieved across multiple chains. The protocol's design has a deeply integrated security against attacks. <br/> 
Having introduced another blockchain, we also introduce a token `xpeer coin`. This is the currency in which the fees are paid. `xpeer coin` heavily bases on `bitcoin` - so it is a minable, fungible token. The protocol is meant to be run over a PoW blockchain.

### Blockchain
In `xpeer` blockchain, blocks are mined every minute and their size is limited to 1MB. Each block consists of transactions, but the protocol approves mining of empty blocks. First transaction in a block is a transaction without inputs which outputs totals to the sum of fees and the value of mining award. Any other transaction must take inputs. `xpeer`'s transactions are quite similar to `bitcoin`'s - they take inputs and produce outputs, which until not spent (or blocked) exist as [UTXOs](https://www.mycryptopedia.com/bitcoin-utxo-unspent-transaction-output-set-explained/).

_NOTE: Although, the protocol is meant to run over a PoW blockchain, the PoC will implement a PoA blockchain (with only one node authorized to mine new blocks) as it simplifies the implementation._

### XPC
`xpeer coin` is the currency in which all transactions on `xpeer` blockchain are being held. It has a total supply of ~100 millions. The smallest denomination of `XPC` is a `bdzys` and equals to `1e-18 XPC`.

### Mining award
This is an extra amount of `xpeer coins` that is can be transferred to a miner's account and together with transaction fees is the incentive for miners to mine. At the beginning of the chain, the award equals to 50 `XPC` and is halved each million of blocks.

### DUTXO and BUTXO 
As said before, the design of the protocol is profoundly influenced by the security of the parts of the exchange. To achieve this, each transaction requires high deposits, which in case of the malicious behaviour are burnt. The deposit is a normal transaction output, but the transaction itself points to the specified output and marks it as a deposit (`DUTXO`). A `DUTXO` cannot be used as a transaction input until the user was proven to have executed its part of the exchange. If a user has acted maliciously, the protocol assumes a `DUTXO` as blocked and therefore a `BUTXO` comes into existence. 

### Transactions

Each transaction (beside first in the block) must take inputs (at least one) and optionally has outputs. The inputs specifies `UTXO`s to be spent and outputs create new `UTXO`s. This is a basic transaction, but the protocol introduces several other types that derive from this basic one.

### Types of transactions allowed by the `xpeer` protocol

#### Simple transfer

   <p align="center">
       <img src="/docs/images/payment_seq.png" />
   </p>

To make a simple transfer user has to specify the amount of money to be sent, the receiver's address and the amount of money to be sent back. Our protocol enables only to send all the owner's funds, so the only one solution is to transfer the rest of money to oneself. There is no restriction related to the quantity of receivers.
Transfer is getting valid when is included in xpeer's blockchain. To make it faster user should leave higher mining fee. Of course,
there is an award for miners when they find a block, but it is slowly decreasing and one day will have become 0. Miners are not obligated to explore blocks,
so without any incentive there is a small possibility to get the transaction involved.


#### Making an offer

   <p align="center">
       <img src="/docs/images/offer_seq.png" />
   </p>

Making an offer is a first step of an exchange. Our protocol treats offers as simple transfers, but they contain more information.
Maker has to specify which currency is being sold and the value, which currency is expected and also value. What is more, user has to provide an address for a payment.
It is widely known that each currency has a specific addresses' lengths, usually different through the range of crypto, so it is also automatically included.
Another important factor are fees (in xpeer currency) - for adding an offer, for confirmation of the offer and the deposit in case of cheating. Offers have more data to process
than simple transfers, so miners have more expensive computations. This is the way to make the offer valid in a blockchain faster - the more mining fee,
the more miners who want to catch it. It is worth mentioning that the offer becomes visible only when is included in xpeer's blockchain. The same with incentive for adding
a confirmation block, which requires the most computations in our protocol. A deposit is a kind of protection for cheating. When the side of exchange plays the game, it is handed back. 
There is also another vital information - timeout. Timeout says how much time an offer is valid and, in case of acceptance, how much time sides have for an exchange then.


#### Taking an offer

   <p align="center">
       <img src="/docs/images/taking_seq.png" />
   </p>

Taking an offer means that one find an offer and is willing to exchange its money. That info makes some kind of a contract between those two sides, each of them agrees to
send funds on time. In our protocol it means that an acceptance transaction is involved into xpeer's blockchain. In addition to inputs and outputs lists, acceptance transaction
contains hash of the offer, specifies taker's address for income and can be created only if matching offer exists in our blockchain. To make an acceptance, user has to send fees
that are the same as in the offer.


#### Transaction's confirmation

Transaction's confirmation is kind of information that both sides of a trade have sent money that they had agreed before. This is necessary for unlocking funds included
in the exchange (each currency will have a mechanism that checks xpeer's blockchain for confirmations when the trade is done) and for getting back the deposit.
Confirmations contain only inputs and outpus and hash of the offer, but requires the most calculations. They are automatically added when an exchange is finished,
but not only depends it on our blockchain but also requires validation of other cryptocurrencies' transactions.
 

#### Unlocking deposit

   <p align="center">
       <img src="/docs/images/unlocking_seq.png" />
   </p>

When at least here one side of exchange does not honor an obligation of sending funds, confirmation is not added into xpeer's blockchain. It means that sides cannot get the
deposit back. The honest one can make an order that verifies its innocence. The order is nothing but verification of sent currency's blockchain to prove that funds
has been sent. Then the result of that research is added into xpeer's blockchain. This kind of commission requires transaction fee and additionally another __deposit__.
That deposit is the same as the one that user want to get back. It is connected with minimization of possible jobs that may overload our network. Unlocking can be done when 
the time for an exchange is out.

In case of unaccepted offer, the way of getting money back is quite similar. Maker has to specify hash of the offer and pay transaction fee and a __deposit__. If there is no 
offer acceptance the deposit and the fee for a confirmation block is unlocked, in other case those deposits and fees are finally blocked. 

Both results are included into xpeer's blockchain as a kind of transaction. 


   <p align="center">
        <img src="/docs/images/exchange_pipe.png" />
   </p>

### UTXO
   There are two types of transactions' outputs:
   
   __1) Simple transfer to given address.__
   
   To unlock it, one have to provide its signature(private key) compatible with public key
   given in previous output.

   __2) Part of an exchange.__ 
   
   Here one has to specify hash of the offer and possible receiver's address and timestamp with address of
   possible return. To unlock that funds there must be a confirmation block of that offer and given receiver's signature or time is out and previous owner's signature. 
   There is a possibility when both sides can unlock that funds - time is over and exchange was confirmed. The current owner has to remember to transfer its money another
   one on time, if not, the previous one can spend it. It eliminates amount of money which is unused.

_NOTE: We as authors inform each user about that possibility and are not responsible for those deceits._

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
   	
   __4) Deposit value__
   
   The deposit's fee has to be __at least 10 times larger__ than a transaction's fee in a block. It is a protocols requirement protecting from cheating and DDoS attack 
   on xpeer's network(steady requests to unlock deposit). Transactions which do not meet this requirement are included in the blockchain, but are not valid and cannot be spent.
   Deposit is always payed in xpeer currency, user has to specify its value while making or taking an offer. In case of innocence verification(Unlocking deposit) deposit value must be
   the same as that to be released or else this operation will be invalid(but those funds will be unreachable).
   
   __5) Timeouts__
   
   <p align="center">
          <img src="/docs/images/timeouts.png" />
   </p>
   
   xpeer, when is involved in an exchange, can be unlocked in two ways:
   
    - the exchange is confirmed and the receiver provides its private key
    - time for the exchange is out and the sender provides its private key
   
   Time for an exchange is specified while making an offer. Timeout says how much time takers have for accepting the offer, then it is becoming unreachable. 
   When the offer is accepted, both sides have the same amount of time to send their funds, starting from the first timeout. One should do it as soon as possible because nobody
   knows how much it takes to send other cryptocurrency. When the second time is out and the exchange is confirmed, both sides can spend this amount of xpeer(as described above).
   __It is crucial for receiver to transfer those funds another one, otherwise can lose it.__ If the exchange is not confirmed, the honest side can make an order to unlock its
   deposit. The same with unlocking deposit and confirmation fee in case of unaccepted offer(also after the second timeout).
    
## Data structures 

   ### 1) Block
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

   ### 2) Transactions
   
   __Simple transaction__
   
   <p align="center">
        <img src="/docs/images/transaction.png" alt="Image" />
   </p>
   

   __Minting__
   
   Minting is a special kind of transaction and it is a model of a decreasing award for mining block. Minting is the only one to have no inputs.
   
   <p align="center">
        <img src="/docs/images/minting.png" alt="Image" />
   </p>

   __Offer__

   <p align="center">
        <img src="/docs/images/offer.png" alt="Image" />
   </p>

   __Acceptance__

   <p align="center">
        <img src="/docs/images/acceptance.png" alt="Image" />
   </p>

   __Confirmation__

   <p align="center">
        <img src="/docs/images/confirmation.png" alt="Image" />
   </p>

   __Unlocking deposit__

   <p align="center">
        <img src="/docs/images/unlocking.png" alt="Image" />
   </p>

   ### 3) Transactions' inputs and outputs
          
   <p align="center">
        <img src="/docs/images/in_out.png" alt="Image" />
   </p>

## System architecture




    
