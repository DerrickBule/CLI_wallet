// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

contract PaymentContract {
    // 记录合约所有者地址
    address public owner;

    constructor() {
        // 部署合约时设置合约所有者为部署者地址
        owner = msg.sender;
    }

    // 接收以太币的函数
    receive() external payable {}

    // 提现函数，只有合约所有者可以调用
    function withdraw(address payable _to, uint256 _amount) external {
        require(msg.sender == owner, "Not owner");
        require(address(this).balance >= _amount, "Insufficient balance");
        _to.transfer(_amount);
    }

    // 获取合约当前余额的函数
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
