# app.py
import os
import sys
import json
import time
import argparse
from typing import Dict, List
from web3 import Web3

DEFAULT_RPC = os.environ.get("RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")

def fetch_tx_count(w3: Web3, address: str, block: str = "latest") -> int:
    """Return transaction count (nonce) for address."""
    return w3.eth.get_transaction_count(address, block_identifier=block)

def fetch_balance(w3: Web3, address: str, block: str = "latest") -> int:
    """Return balance in wei for address."""
    return w3.eth.get_balance(address, block_identifier=block)

def analyze_accounts(w3: Web3, addresses: List[str], block: str) -> Dict[str, Dict[str, int]]:
    results = {}
    for addr in addresses:
                # ✅ New: Print progress for each account being analyzed
        print(f"🔍 Fetching data for {addr} ...")
        try:
            bal = fetch_balance(w3, addr, block)
            txs = fetch_tx_count(w3, addr, block)
            results[addr] = {"balance_wei": bal, "tx_count": txs}
        except Exception as e:
            results[addr] = {"error": str(e)}
    return results

def compare_states(a: Dict[str, Dict[str, int]], b: Dict[str, Dict[str, int]]) -> List[str]:
    """Compare account balances and tx counts between A and B."""
    diffs = []
    for addr in sorted(set(a.keys()) | set(b.keys())):
        va, vb = a.get(addr, {}), b.get(addr, {})
        if va != vb:
            diffs.append(addr)
    return diffs

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="zk-account-soundness — compare account balances and nonce state between two RPCs or blocks for zk and web3 audits."
    )
    p.add_argument("--rpc-a", default=DEFAULT_RPC, help="Primary RPC (default from RPC_URL)")
    p.add_argument("--rpc-b", required=True, help="Secondary RPC to compare against")
    p.add_argument("--address", action="append", required=True, help="Account address (repeatable)")
    p.add_argument("--block-a", default="latest", help="Block number/tag for RPC A (default: latest)")
    p.add_argument("--block-b", default="latest", help="Block number/tag for RPC B (default: latest)")
    p.add_argument("--json", action="store_true", help="Emit results in JSON format")
    p.add_argument("--timeout", type=int, default=30, help="RPC timeout seconds (default: 30)")
    return p.parse_args()

def main() -> None:
    args = parse_args()

    for rpc in [args.rpc_a, args.rpc_b]:
        if not str(rpc).startswith(("http://", "https://")):
            print(f"❌ Invalid RPC URL: {rpc}")
            sys.exit(1)

    addrs = []
    for a in args.address:
        if not Web3.is_address(a):
            print(f"❌ Invalid address: {a}")
            sys.exit(1)
        addrs.append(Web3.to_checksum_address(a))

    w3a = Web3(Web3.HTTPProvider(args.rpc_a, request_kwargs={"timeout": args.timeout}))
    w3b = Web3(Web3.HTTPProvider(args.rpc_b, request_kwargs={"timeout": args.timeout}))

    if not w3a.is_connected() or not w3b.is_connected():
        print("❌ Failed to connect to one or both RPCs.")
        sys.exit(1)

    print("🔧 zk-account-soundness")
    print(f"🔗 RPC A: {args.rpc_a}")
    print(f"🔗 RPC B: {args.rpc_b}")
    print(f"🧱 Block A: {args.block_a} | Block B: {args.block_b}")
    print(f"👥 Accounts: {len(addrs)}")
    from datetime import datetime
    print(f"🕒 Comparison Timestamp: {datetime.utcnow().isoformat()}Z")

    start = time.time()
    state_a = analyze_accounts(w3a, addrs, args.block_a)
    state_b = analyze_accounts(w3b, addrs, args.block_b)
    diffs = compare_states(state_a, state_b)
    elapsed = round(time.time() - start, 2)

    print("\n📊 Results:")
    for addr in addrs:
        a = state_a.get(addr, {})
        b = state_b.get(addr, {})
        match = "✅ MATCH" if a == b else "❌ DIFF"
        bal_a = a.get("balance_wei", "ERR")
        bal_b = b.get("balance_wei", "ERR")
        txa = a.get("tx_count", "ERR")
        txb = b.get("tx_count", "ERR")
        print(f"  • {addr}: Balance {bal_a} vs {bal_b}, TXs {txa} vs {txb} → {match}")

    if not diffs:
        print("\n🎯 Account states match across both RPCs.")
    else:
        print(f"\n🚨 {len(diffs)} account(s) differ between the two sources.")

    if args.json:
        out = {
            "rpc_a": args.rpc_a,
            "rpc_b": args.rpc_b,
            "block_a": args.block_a,
            "block_b": args.block_b,
            "addresses": addrs,
            "state_a": state_a,
            "state_b": state_b,
            "diffs": diffs,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "elapsed_seconds": elapsed,
            "ok": len(diffs) == 0,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))

    sys.exit(0 if not diffs else 2)

if __name__ == "__main__":
    main()
