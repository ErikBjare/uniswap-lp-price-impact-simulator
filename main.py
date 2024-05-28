"""
This script demonstrates how to simulate adding extra liquidity providers to a pool and checking the price impact.

To add the extra liquidity providers we use a fork of mainnet, minting tokens for the extra LPs and adding them to the pool.
"""

from uniswap import Uniswap
from uniswap.util import encode_sqrt_ratioX96, get_tick_at_sqrt
from web3 import Web3

# tokens
grow = Web3.to_checksum_address("0x761a3557184cbc07b7493da0661c41177b2f97fa")
dai = Web3.to_checksum_address("0x6b175474e89094c44da98b954eedeac495271d0f")

# hardhat
account1_pub = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
account1_priv = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# LP positions to add to the pool
# low and high are the price range in USD
lp_positions = [
    # {"low": 0.09, "high": 4.41, "grow": 209303, "eth": 183.18},
    # {"low": 1.25, "high": 12.46, "grow": 128548, "eth": 11.26},
    # FIXME: sometimes I get errors when `"eth": 0` is used, I don't get why.
    {"low": 1.50, "high": 1.70, "grow": 85000, "eth": 1},
    {"low": 1.70, "high": 2.10, "grow": 125000, "eth": 1},
    {"low": 2.10, "high": 2.50, "grow": 125000, "eth": 0},
    {"low": 2.50, "high": 2.90, "grow": 125000, "eth": 0},
    {"low": 2.90, "high": 3.40, "grow": 125000, "eth": 0},
    {"low": 3.40, "high": 10.00, "grow": 500000, "eth": 0},
    {"low": 10.00, "high": 30.00, "grow": 500000, "eth": 0},
]

lp_positions_scenario_1 = [
    {"low": 1.60, "high": 1.90, "grow": 450000, "eth": 1},
    {"low": 1.90, "high": 2.30, "grow": 400000, "eth": 0},
    {"low": 2.30, "high": 2.70, "grow": 300000, "eth": 0},
    {"low": 2.70, "high": 3.10, "grow": 200000, "eth": 0},
    {"low": 3.10, "high": 3.50, "grow": 150000, "eth": 0},
]

lp_positions_scenario_2 = [
    {"low": 1.60, "high": 1.90, "grow": 500000, "eth": 1},
    {"low": 1.90, "high": 2.30, "grow": 450000, "eth": 0},
    {"low": 2.30, "high": 2.70, "grow": 350000, "eth": 0},
    {"low": 2.70, "high": 3.10, "grow": 200000, "eth": 0},
]

lp_positions_scenario_3 = [
    {"low": 1.60, "high": 1.90, "grow": 550000, "eth": 1},
    {"low": 1.90, "high": 2.30, "grow": 500000, "eth": 0},
    {"low": 2.30, "high": 2.70, "grow": 450000, "eth": 0},
]

lp_positions_scenario_4 = [
    {"low": 1.60, "high": 1.90, "grow": 800000, "eth": 1},
    {"low": 1.90, "high": 2.30, "grow": 700000, "eth": 0},
]


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

    # groweth pool fee
    fee = 10000

    weth = uniswap.get_weth_address()
    print("Connected to Uniswap v3")
    ethusd = uniswap.get_price_output(dai, weth, 10**18, fee=3000) / 10**18
    print(f"ETH price: ${ethusd}")
    growusd = (
        ethusd * uniswap.get_price_output(weth, grow, 10**18, fee=fee) / 10**18
    )
    print(f"GROW price: ${growusd}")

    eth_bal = uniswap.get_eth_balance()
    print(f"ETH balance: {eth_bal}")
    for token in [weth, grow]:
        bal = uniswap.get_token_balance(token)
        print(f"{token} balance: {bal}")

    def _print_poolstate():
        # Price for GROW buys
        for qty in (10**exp * 10**18 for exp in [3, 4, 5]):
            price = uniswap.get_price_output(weth, grow, int(qty), fee=fee)
            print(f"Price for buying {qty / 10**18} GROW: {price / 10**18} ETH")

        # Impact for GROW sells
        for eth_qty in (10**exp * 10**18 for exp in [0, 1, 2.5]):
            try:
                qty = uniswap.get_price_output(grow, weth, int(eth_qty), fee=fee)
                impact = uniswap.estimate_price_impact(grow, weth, qty, fee=fee)
                print(
                    f"Impact on v3 for selling {eth_qty / 10**18} ETH worth of GROW:  {_perc(impact)}"
                )
            except Exception as e:
                print(f"Error: {e}")

        # Impact for ETH buys
        for qty in (10**exp * 10**18 for exp in range(4)):
            impact = uniswap.estimate_price_impact(weth, grow, qty, fee=fee)
            dollars = round(qty / 10**18 * ethusd)
            print(
                f"Impact on v3 for buying with {qty / 10**18} ETH (${dollars:,}):  {_perc(impact)}"
            )

        # Impact for GROW buys
        for qty in (15 * 10**exp * 10**18 for exp in [4, 5, 6]):
            impact = uniswap.estimate_price_impact(grow, weth, qty, fee=fee)
            dollars = round(qty / 10**18 * growusd)
            print(
                f"Impact on v3 for buying {qty / 10**18} GROW (${dollars:,}):  {_perc(impact)}"
            )

    print("\nBefore:")
    _print_poolstate()

    print()

    pool = uniswap.get_pool_instance(grow, weth, fee)
    print(f"Pool contract: {pool.address}")
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
        tick_low = get_tick_at_sqrt(pos_low_sqrt)
        tick_high = get_tick_at_sqrt(pos_high_sqrt)
        print(f"Adding LP position: {pos}")
        # print(f"  price_low: {decode_sqrt_ratioX96(pos_low_sqrt)}, tick_range: ({tick_low}, {tick_high})")
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
