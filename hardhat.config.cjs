/** @type import('hardhat/config').HardhatUserConfig */
require("dotenv").config();
require("@nomicfoundation/hardhat-ethers");

module.exports = {
  networks: {
    hardhat: {
      forking: {
        url: process.env.PROVIDER,
      },
      chainId: 1,
    },
    fork: {
      url: "http://127.0.0.1:10999",
      chainId: 1,
    },
  },
  solidity: "0.8.24",
};
