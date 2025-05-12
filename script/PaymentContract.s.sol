// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/PaymentContract.sol";

contract PaymentContractScript is Script {
    function run() external returns (PaymentContract) {
        uint256 privateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(privateKey);
        PaymentContract paymentContract = new PaymentContract();
        vm.stopBroadcast();
        return paymentContract;
    }
}
