from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from base58 import b58decode
import asyncio

# Connect to Solana blockchain
client = Client("https://api.mainnet-beta.solana.com")

# Load wallet from a private key (ensure you handle private keys securely!)
def load_wallet(private_key: str) -> Keypair:
    decoded_key = b58decode(private_key)
    return Keypair.from_secret_key(decoded_key)

# Fetch wallet balance
def get_balance(public_key: PublicKey):
    balance = client.get_balance(public_key)
    if balance['result']:
        lamports = balance['result']['value']
        sol = lamports / 1_000_000_000  # Convert lamports to SOL
        return sol
    else:
        raise Exception("Failed to fetch balance")

# Transfer funds
async def send_funds(sender_keypair: Keypair, recipient_address: str, amount: float):
    async with AsyncClient("https://api.mainnet-beta.solana.com") as async_client:
        recipient = PublicKey(recipient_address)
        lamports = int(amount * 1_000_000_000)  # Convert SOL to lamports
        
        # Create a transaction
        transaction = Transaction()
        transaction.add(
            transfer(
                TransferParams(
                    from_pubkey=sender_keypair.public_key,
                    to_pubkey=recipient,
                    lamports=lamports,
                )
            )
        )
        
        # Sign the transaction
        try:
            signed_transaction = transaction.sign([sender_keypair])
            signature = await async_client.send_transaction(signed_transaction, sender_keypair)
            print(f"Transaction successful with signature: {signature}")
        except Exception as e:
            print(f"Failed to send funds: {e}")

# Main function
def main():
    private_key = input("Enter your private key: ")
    sender_wallet = load_wallet(private_key)
    
    print("Your wallet address:", sender_wallet.public_key)
    print("Your balance:", get_balance(sender_wallet.public_key), "SOL")
    
    recipient_address = input("Enter recipient wallet address: ")
    amount = float(input("Enter amount of SOL to send: "))
    
    print("Sending funds...")
    asyncio.run(send_funds(sender_wallet, recipient_address, amount))

if __name__ == "__main__":
    main()
