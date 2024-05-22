"""
This script demonstrates how to simulate adding extra liquidity providers to a pool and checking the price impact.

To add the extra liquidity providers we use a fork of mainnet, minting tokens for the extra LPs and adding them to the pool.
"""

from uniswap import Uniswap
from uniswap.util import encode_sqrt_ratioX96, get_tick_at_sqrt
from web3 import Web3

eth = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")
grow = Web3.to_checksum_address("0x761a3557184cbc07b7493da0661c41177b2f97fa")

# LP positions to add to the pool
lp_positions = [
    {"low": 0.09, "high": 4.41, "grow": 209303, "eth": 183.18},
    {"low": 1.25, "high": 12.46, "grow": 128548, "eth": 11.26},
    {"low": 1.50, "high": 1.70, "grow": 85000, "eth": 0},
    {"low": 1.70, "high": 2.10, "grow": 125000, "eth": 0},
    {"low": 2.10, "high": 2.50, "grow": 125000, "eth": 0},
    {"low": 2.50, "high": 2.90, "grow": 125000, "eth": 0},
    {"low": 2.90, "high": 3.40, "grow": 125000, "eth": 0},
    {"low": 3.40, "high": 10.00, "grow": 500000, "eth": 0},
    {"low": 10.00, "high": 30.00, "grow": 500000, "eth": 0},
]


def _perc(f: float) -> str:
    return f"{round(f * 100, 3)}%"


def simulate():
    """
    Simulate adding extra liquidity providers to a pool and check the price impact.
    """
    # start ganache with:
    # ganache --port 10999 --wallet.seed test --chain.networkId 1 --chain.chainId 1 --fork.url $PROVIDER
    # npx hardhat node --port 10099 --fork $PROVIDER

    if True:
        # hardhat
        account1_pub = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        account1_priv = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
    if False:
        # ganache
        account1_pub = "0x94e3361495bD110114ac0b6e35Ed75E77E6a6cFA"
        account1_priv = (
            "0x6f1313062db38875fb01ee52682cbf6a8420e92bfbc578c5d4fdc0a32c50266f"
        )
    uniswap = Uniswap(
        address=account1_pub,
        private_key=account1_priv,
        version=3,
        provider="http://127.0.0.1:10999",
    )
    weth = uniswap.get_weth_address()

    print("Connected to Uniswap v3")
    eth_bal = uniswap.get_eth_balance()
    print(f"ETH balance: {eth_bal}")
    weth_bal = uniswap.get_token_balance(weth)
    print(f"WETH balance: {weth_bal}")
    grow_bal = uniswap.get_token_balance(grow)
    print(f"GROW balance: {grow_bal}")

    print("Getting the pool instance")
    pool = uniswap.get_pool_instance(weth, grow, 10000)
    print(pool)

    print("Adding extra LPs to the pool")

    for pos in lp_positions:
        amount_grow = int(pos["grow"] * 10**18)
        amount_eth = int(pos["eth"] * 10**18)
        tick_low = get_tick_at_sqrt(
            encode_sqrt_ratioX96(10**18, int(pos["low"] * 10**18))
        )
        tick_high = get_tick_at_sqrt(
            encode_sqrt_ratioX96(10**18, int(pos["high"] * 10**18))
        )
        print(f"Adding LPs with positions: {pos}")
        print(f"Adding {amount_grow} GROW and {amount_eth} ETH")
        uniswap.mint_liquidity(
            pool,
            amount_0=amount_grow,
            amount_1=amount_eth,
            tick_lower=tick_low,
            tick_upper=tick_high,
        )

    # Compare the results with the output of:
    qty = 1 * 10**18
    impact = uniswap.estimate_price_impact(eth, grow, qty, fee=10000)
    print(f"Impact for buying on v3 with {qty / 10**18} ETH:  {_perc(impact)}")

    qty = 100 * 10**18
    impact = uniswap.estimate_price_impact(eth, grow, qty, fee=10000)
    print(f"Impact for buying on v3 with {qty / 10**18} ETH:  {_perc(impact)}")

    print(
        "Compare with:"
        f"https://app.uniswap.org/#/swap?use=v3&inputCurrency=ETH&outputCurrency={grow}"
    )


if __name__ == "__main__":
    simulate()
