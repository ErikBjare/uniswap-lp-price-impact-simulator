"""
This script demonstrates how to simulate adding extra liquidity providers to a pool and checking the price impact.

To add the extra liquidity providers we use a fork of mainnet, minting tokens for the extra LPs and adding them to the pool.
"""

from uniswap import Uniswap
from uniswap.util import decode_sqrt_ratioX96, encode_sqrt_ratioX96, get_tick_at_sqrt
from web3 import Web3

# tokens
grow = Web3.to_checksum_address("0x761a3557184cbc07b7493da0661c41177b2f97fa")

# hardhat
account1_pub = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
account1_priv = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# LP positions to add to the pool
# low and high are the price range in USD
lp_positions = [
    {"low": 0.09, "high": 4.41, "grow": 209303, "eth": 183.18},
    {"low": 1.25, "high": 12.46, "grow": 128548, "eth": 11.26},
    {"low": 1.50, "high": 1.70, "grow": 85000, "eth": 1},
    {"low": 1.70, "high": 2.10, "grow": 125000, "eth": 0},
    {"low": 2.10, "high": 2.50, "grow": 125000, "eth": 0},
    {"low": 2.50, "high": 2.90, "grow": 125000, "eth": 0},
    {"low": 2.90, "high": 3.40, "grow": 125000, "eth": 0},
    {"low": 3.40, "high": 10.00, "grow": 500000, "eth": 0},
    {"low": 10.00, "high": 30.00, "grow": 500000, "eth": 0},
]

ethusd = 3700


def _perc(f: float) -> str:
    return f"{round(f * 100, 3)}%"


def simulate():
    """
    Simulate adding extra liquidity providers to a pool and check the price impact.
    """
    uniswap = Uniswap(
        address=account1_pub,
        private_key=account1_priv,
        version=3,
        provider="http://127.0.0.1:10999",
    )
    fee = 10000
    weth = uniswap.get_weth_address()
    print("Connected to Uniswap v3")
    print(f"Assuming ETH price: ${ethusd}")

    eth_bal = uniswap.get_eth_balance()
    print(f"ETH balance: {eth_bal}")
    for token in [weth, grow]:
        bal = uniswap.get_token_balance(token)
        print(f"{token} balance: {bal}")

    def _print_poolstate():
        for qty in (10**exp * 10**18 for exp in range(3, 9, 3)):
            price = uniswap.get_price_output(weth, grow, qty, fee=fee)
            print(f"Price for buying {qty / 10**18} GROW in ETH: {price}")

        for qty in (10**exp * 10**18 for exp in range(4)):
            impact = uniswap.estimate_price_impact(weth, grow, qty, fee=fee)
            print(f"Impact for buying on v3 with {qty / 10**18} ETH:  {_perc(impact)}")

    print("\nBefore:")
    _print_poolstate()

    print()
    print("Now we add extra LPs to the pool")

    print("Getting the pool instance")
    pool = uniswap.get_pool_instance(grow, weth, fee)
    print(pool)

    print("Adding extra LPs to the pool")
    for pos in lp_positions:
        amount_grow = int(pos["grow"] * 10**18)
        amount_eth = int(pos["eth"] * 10**18)
        pos_low_sqrt = encode_sqrt_ratioX96(
            10**18, int(pos["low"] / ethusd * 10**18)
        )
        pos_high_sqrt = encode_sqrt_ratioX96(
            10**18, int(pos["high"] / ethusd * 10**18)
        )
        price_low = decode_sqrt_ratioX96(pos_low_sqrt)
        tick_low = get_tick_at_sqrt(pos_low_sqrt)
        tick_high = get_tick_at_sqrt(pos_high_sqrt)
        print(f"Adding LP position: {pos}")
        print(f"  price_low: {price_low}, tick_range: ({tick_low}, {tick_high})")
        uniswap.mint_liquidity(
            pool,
            amount_0=amount_grow,
            amount_1=amount_eth,
            tick_lower=tick_low,
            tick_upper=tick_high,
        )

    position_array = uniswap.get_liquidity_positions()
    print(f"LP positions: {position_array}")

    print("\nAfter:")
    _print_poolstate()

    print(
        "Compare with current rates: "
        f"https://app.uniswap.org/#/swap?use=v3&inputCurrency=ETH&outputCurrency={grow}"
    )


if __name__ == "__main__":
    simulate()
