import os
import json
import base64
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class LedgerManager:
    """
    Manages the Encrypted Local Mutation Ledger (DML).
    Uses AES-256-GCM for authenticated encryption.
    """
    def __init__(self, storage_path=None, secret_key="collaborative-fc-default-key"):
        if storage_path is None:
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            storage_path = os.path.join(appdata, 'CollaborativeFC', 'mutation_ledger.dml')
        
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # In a real app, the key would be derived from a user password or PKI
        self.key = self._derive_key(secret_key)
        self.aesgcm = AESGCM(self.key)

    def _derive_key(self, password):
        """Derives a 32-byte key from a password using PBKDF2."""
        salt = b'synergy-salt-123' # In production, use a unique stored salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def append_mutation(self, author_id, obj_name, prop_name, value):
        """Appends a new mutation to the encrypted ledger."""
        mutation = {
            "id": os.urandom(8).hex(),
            "author": author_id,
            "object": obj_name,
            "property": prop_name,
            "value": value,
            "timestamp": time.time()
        }
        
        # Serialize to JSON
        data = json.dumps(mutation).encode()
        
        # Encrypt with AES-GCM (nonce must be unique per encryption)
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        
        # Store as [nonce(12)][ciphertext] in append mode
        with open(self.storage_path, "ab") as f:
            # We store the length prefix to distinguish entries in the flat file
            entry = nonce + ciphertext
            f.write(len(entry).to_bytes(4, byteorder='big'))
            f.write(entry)
            
        return mutation["id"]

    def read_all_mutations(self):
        """Decrypts and returns all mutations in the ledger."""
        mutations = []
        if not os.path.exists(self.storage_path):
            return mutations
            
        with open(self.storage_path, "rb") as f:
            while True:
                length_bytes = f.read(4)
                if not length_bytes:
                    break
                length = int.from_bytes(length_bytes, byteorder='big')
                entry = f.read(length)
                
                nonce = entry[:12]
                ciphertext = entry[12:]
                
                try:
                    data = self.aesgcm.decrypt(nonce, ciphertext, None)
                    mutations.append(json.loads(data.decode()))
                except Exception as e:
                    print(f"Decryption failed for entry: {e}")
                    
        return mutations

if __name__ == "__main__":
    # Quick Test
    lm = LedgerManager("test_ledger.dml")
    mid = lm.append_mutation("p1", "Body001", "Length", 50.0)
    print(f"Recorded Mutation: {mid}")
    
    all_m = lm.read_all_mutations()
    print(f"Decrypted Ledger: {all_m}")
    os.remove("test_ledger.dml")
