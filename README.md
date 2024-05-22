Scripts for simulating adding LP positions to a Uniswap pool and checking how it affects price impact.


# Usage

```sh
# install deps
npm install
poetry install

# set up fork of mainnet
npx hardhat node --port 10999

# transfer grow by impersonating treasury
npx hardhat run scripts/transfer-grow.js --network fork

# add LPs and check price imact
poetry run python3 main.py
```
