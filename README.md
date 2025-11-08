# zk-account-soundness

## Overview
`zk-account-soundness` compares **account balances and transaction counts (nonces)** between two RPC endpoints or block heights.  
It’s a lightweight tool for verifying **cross-chain or multi-node state consistency**, which is vital for zk systems, bridge contracts, or replicated rollup verifiers.

## Features
- Compares multiple accounts across two RPCs or blocks  
- Checks both balances and nonces (transaction counts)  
- Detects discrepancies between nodes or chains  
- Emits JSON for CI automation or zk validation pipelines  
- Simple exit codes for integration (0 = OK, 2 = mismatch)  
- Timestamped results for reproducibility  

## Installation
1. Python 3.9+  
2. Install dependency:
   pip install web3  
3. (Optional) Export your default RPCs:
   export RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY  

## Usage
Compare two RPC endpoints for the same account:
   python app.py --rpc-a https://mainnet.infura.io/v3/YOUR_KEY --rpc-b https://arb1.arbitrum.io/rpc --address 0xYourAddress

Compare multiple accounts (repeat --address):
   python app.py --rpc-a https://eth.llamarpc.com --rpc-b https://base.llamarpc.com --address 0xA --address 0xB

Compare across different blocks on the same RPC:
   python app.py --rpc-a https://mainnet.infura.io/v3/YOUR_KEY --rpc-b https://mainnet.infura.io/v3/YOUR_KEY --address 0xA --block-a 19000000 --block-b 20000000

Emit JSON for machine-readable results:
   python app.py --rpc-a ... --rpc-b ... --address 0xA --json

Increase timeout for slower RPCs:
   python app.py --address 0xA --rpc-b https://custom.rpc --timeout 60

## Example Output
🔧 zk-account-soundness  
🔗 RPC A: https://mainnet.infura.io/v3/...  
🔗 RPC B: https://arb1.arbitrum.io/rpc  
🧱 Block A: latest | Block B: latest  
👥 Accounts: 2  
🕒 Comparison Timestamp: 2025-11-08T17:12:04Z  

📊 Results:  
  • 0x0000000000000000000000000000000000000000: Balance 0 vs 0, TXs 0 vs 0 → ✅ MATCH  
  • 0xAbC123...567: Balance 1042000000000000000 vs 1042000000000000000, TXs 15 vs 15 → ✅ MATCH  

🎯 Account states match across both RPCs.  

## Notes
- **Purpose:** Helps detect RPC drift, replay lag, or fork inconsistencies between nodes.  
- **ZK Integrity:** Ensures state equality before generating zk-proofs or synchronizing bridges.  
- **Cross-chain Safety:** Ideal for verifying asset lock/release equivalence on L1–L2 bridges.  
- **Nonces:** Useful for confirming sequencer synchronization in rollups.  
- **Archive RPCs:** For historical blocks, ensure your provider supports archive mode.  
- **Timestamps:** Each run logs a UTC timestamp to help trace test events over time.  
- **Automation:** Perfect for scheduled CI checks, nightly validations, or zk verifier audits.  

## Exit Codes
0 → All accounts matched  
2 → One or more mismatches or connection
