import os
from web3 import Web3
from eth_account import Account
from api.database import create_tables, SessionLocal
from api.services import save_transaction
import config
# 连接到以太坊节点，这里以 Sepolia 测试网为例
w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
if not w3.is_connected():
    print("无法连接到以太坊节点，请检查网络配置")
    exit(1)

# 创建数据库表
create_tables()

# 合约 ABI
CONTRACT_ABI = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"getBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]
# 合约地址
contract_address = Web3.to_checksum_address(config.contract_address)
# 初始化合约实例
contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)

def generate_new_account():
    """生成新的以太坊账户"""
    account = Account.create()
    private_key = account.key.hex()
    address = account.address
    return private_key, address

def get_balance(address):
    """查询账户余额"""
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    return balance_wei, balance_eth

# 外部账户私钥和地址
external_private_key = config.external_private_key
external_account = Account.from_key(external_private_key)

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
    
    # 构建基础交易
    tx = {
        'nonce': nonce,
        'to': contract_address,
        'value': amount,
        'maxFeePerGas': max_fee_per_gas,
        'maxPriorityFeePerGas': max_priority_fee_per_gas,
        'chainId': w3.eth.chain_id
    }
    
    try:
        # 估算所需的 gas
        estimated_gas = w3.eth.estimate_gas(tx)
        # 添加 20% 的缓冲
        tx['gas'] = int(estimated_gas * 1.2)
    except Exception as e:
        print(f"估算 gas 时出错: {str(e)}")
        # 如果估算失败，使用一个较大的默认值
        tx['gas'] = 300000
    
    return tx

def save_transaction_to_db(tx_receipt, transaction_type):
    """保存交易数据到数据库"""
    db = SessionLocal()
    try:
        # 获取原始交易数据
        tx = w3.eth.get_transaction(tx_receipt.transactionHash)
        
        save_transaction(
            db=db,
            tx_hash=tx_receipt.transactionHash.hex(),
            block_number=tx_receipt.blockNumber,
            from_address=tx['from'],
            to_address=tx['to'],
            value=tx['value'],
            gas_used=tx_receipt.gasUsed,
            gas_price=tx['gasPrice'],
            status=tx_receipt.status == 1,
            transaction_type=transaction_type
        )
    finally:
        db.close()

if __name__ == '__main__':
    try:
        # 要存入的金额，单位为 Wei
        deposit_amount = Web3.to_wei(0.0001, 'ether')

        # 获取当前nonce
        nonce = w3.eth.get_transaction_count(external_account.address)
        
        # 获取当前gas价格
        gas_price = w3.eth.gas_price
        # 增加10%的gas价格以确保交易能被接受
        gas_price = int(gas_price * 1.1)

        # 构建交易 - 直接发送ETH到合约地址
        tx = {
            'from': external_account.address,
            'to': contract_address,
            'value': deposit_amount,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': gas_price
        }

        # 签名交易
        signed_tx = external_account.sign_transaction(tx)

        # 发送交易
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"\n存款交易哈希: {tx_hash.hex()}")

        # 等待交易确认
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"存款交易确认，区块号: {tx_receipt.blockNumber}")
        print(f"实际使用的 gas: {tx_receipt.gasUsed}")

        # 保存存款交易到数据库
        save_transaction_to_db(tx_receipt, 'deposit')

        # 查询合约中的余额
        contract_balance = contract.functions.getBalance().call()
        print(f"合约中的余额: {Web3.from_wei(contract_balance, 'ether')} ETH")

        # 提现操作
        print("\n开始提现操作...")
        # 检查是否是合约所有者
        owner = contract.functions.owner().call()
        if owner.lower() != external_account.address.lower():
            print(f"错误：当前账户不是合约所有者。合约所有者地址: {owner}")
        else:
            # 获取新的nonce
            nonce = w3.eth.get_transaction_count(external_account.address)
            # 获取新的gas价格并增加10%
            gas_price = int(w3.eth.gas_price * 1.1)
            
            # 构建提现交易
            withdraw_amount = contract_balance  # 提取全部余额
            withdraw_tx = contract.functions.withdraw(
                external_account.address,  # 提现到当前账户
                withdraw_amount
            ).build_transaction({
                'from': external_account.address,
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': gas_price
            })

            # 签名提现交易
            signed_withdraw_tx = external_account.sign_transaction(withdraw_tx)

            # 发送提现交易
            withdraw_tx_hash = w3.eth.send_raw_transaction(signed_withdraw_tx.raw_transaction)
            print(f"提现交易哈希: {withdraw_tx_hash.hex()}")

            # 等待提现交易确认
            withdraw_receipt = w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
            print(f"提现交易确认，区块号: {withdraw_receipt.blockNumber}")
            print(f"实际使用的 gas: {withdraw_receipt.gasUsed}")

            # 保存提现交易到数据库
            save_transaction_to_db(withdraw_receipt, 'withdraw')

            # 再次查询合约余额
            final_balance = contract.functions.getBalance().call()
            print(f"提现后合约中的余额: {Web3.from_wei(final_balance, 'ether')} ETH")

    except Exception as e:
        print(f"交易执行出错: {str(e)}")

    