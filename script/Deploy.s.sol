// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/Bank.sol";
import "@safe-global/safe-contracts/contracts/Safe.sol";
import "@safe-global/safe-contracts/contracts/proxies/SafeProxyFactory.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // 部署 ERC20 Token
        MyToken token = new MyToken();
        
        // 部署 Bank 合约
        Bank bank = new Bank(address(token));

        // 部署 Safe 合约工厂
        SafeProxyFactory factory = new SafeProxyFactory();
        
        // 创建多签钱包
        address[] memory owners = new address[](3);
        owners[0] = vm.envAddress("OWNER1");
        owners[1] = vm.envAddress("OWNER2");
        owners[2] = vm.envAddress("OWNER3");
        
        Safe safe = new Safe();
        
        bytes memory initializer = abi.encodeWithSelector(
            Safe.setup.selector,
            owners,           // owners
            2,                // threshold
            address(0),       // to
            "",              // data
            address(0),       // fallbackHandler
            address(0),       // paymentToken
            0,               // payment
            address(0)        // paymentReceiver
        );
        
        SafeProxy safeProxy = factory.createProxy(address(safe), initializer);
        
        vm.stopBroadcast();
    }
} 