import os
from web3 import Web3
from eth_account import Account

import config

# 连接到以太坊节点，这里以 Sepolia 测试网为例
w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
if not w3.is_connected():
    print("无法连接到以太坊节点，请检查网络配置")
    exit(1)

# 外部账户私钥和地址
external_private_key = config.external_private_key
external_account = Account.from_key(external_private_key)

# 合约地址
contract_address = Web3.to_checksum_address(config.contract_address)

# 构建向合约存款的交易
def build_deposit_transaction(
    w3: Web3,
    sender: str,
    contract_address: str,
    amount: int
):
    nonce = w3.eth.get_transaction_count(sender)
    gas_price = w3.eth.gas_price
    max_priority_fee_per_gas = w3.eth.max_priority_fee
    max_fee_per_gas = max_priority_fee_per_gas + gas_price
    tx = {
        'nonce': nonce,
        'to': contract_address,
        'value': amount,
        'gas': 21000,
        'maxFeePerGas': max_fee_per_gas,
        'maxPriorityFeePerGas': max_priority_fee_per_gas,
        'chainId': w3.eth.chain_id
    }
    return tx

# 要存入的金额，单位为 Wei
deposit_amount = Web3.to_wei(0.000001, 'ether')

# 构建交易
tx = build_deposit_transaction(w3, external_account.address, contract_address, deposit_amount)

# 签名交易
signed_tx = external_account.sign_transaction(tx)

# 发送交易
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"交易哈希: {tx_hash.hex()}")

# 等待交易确认
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"交易确认，区块号: {tx_receipt.blockNumber}")