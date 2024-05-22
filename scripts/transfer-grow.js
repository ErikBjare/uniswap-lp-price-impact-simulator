import hre from "hardhat";

const provider = new hre.ethers.JsonRpcProvider("http://127.0.0.1:10999");
const pubKey = await hre.ethers.getSigner(
  "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
);
const privateKey =
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
const wallet = new ethers.Wallet(privateKey, provider);

async function main() {
  const growTokenAddress = "0x761a3557184cbc07b7493da0661c41177b2f97fa"; // Actual GROW token address
  const impersonatedAccount = "0xD920E60b798A2F5a8332799d8a23075c9E77d5F8"; // ValleyDAO Treasury

  console.log("Impersonating account");
  await hre.network.provider.request({
    method: "hardhat_impersonateAccount",
    params: [impersonatedAccount],
  });
  const impersonatedSigner = await hre.ethers.getSigner(impersonatedAccount);

  console.log("Getting GROW token contract");
  const growToken = await hre.ethers.getContractAt(
    "IERC20",
    growTokenAddress,
    impersonatedSigner
  );

  console.log("Transferring GROW tokens");
  const amount = hre.ethers.parseUnits("1000000", 18); // 1,000,000 GROW tokens
  //await growToken.transfer(pubKey.address, amount);

  console.log(`Transferred ${amount} GROW to ${pubKey.address}`);

  console.log("Wrapping ETH into WETH");
  // Specify the amount of ETH you want to wrap
  await wrapETH(hre.ethers.parseEther("1000"))
    .then(() => console.log("ETH successfully wrapped into WETH"))
    .catch((error) => console.error("Error wrapping ETH into WETH:", error));
}

async function wrapETH(wei) {
  const WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2";
  const WETH_ABI = ["function deposit() public payable"];
  const wethContract = new hre.ethers.Contract(WETH_ADDRESS, WETH_ABI, wallet);

  // Call the deposit function to wrap ETH into WETH
  const tx = await wethContract.deposit({ value: wei });

  console.log(`Transaction hash: ${tx.hash}`);

  // Wait for the transaction to be mined
  await tx.wait();

  console.log(`Wrapped ${wei} wei`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
