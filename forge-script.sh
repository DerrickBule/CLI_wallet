# 加载环境变量
source .env

# 部署并开源合约
forge script script/PaymentContract.s.sol:PaymentContractScript --rpc-url $SEPOLIA_RPC_URL --private-key $PRIVATE_KEY --broadcast --verify --etherscan-api-key $ETHERSCAN_API_KEY -vvvv
forge script script/PaymentContract.s.sol:PaymentContractScript --rpc-url $SEPOLIA_RPC_URL --private-key $PRIVATE_KEY --broadcast --verify --etherscan-api-key $ETHERSCAN_API_KEY -vvvv
