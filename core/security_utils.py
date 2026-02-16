"""
Security Utils para Cleudocode
==============================

Implementa criptografia AES-256 para tokens e credenciais sensíveis.
"""

import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

class SecurityManager:
    def __init__(self, password: str = None):
        # Usa o GATEWAY_TOKEN como base para a chave se nenhuma senha for fornecida
        if not password:
            password = os.getenv("CLEUDOCODE_GATEWAY_TOKEN", "default-secret-key").encode()
        else:
            password = password.encode()
            
        salt = b'cleudo_salt_fixed' # Em produção usaríamos um salt dinâmico guardado
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        if not data: return ""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        if not token: return ""
        return self.fernet.decrypt(token.encode()).decode()

# Global Instance
security = SecurityManager()

if __name__ == "__main__":
    test_data = "MinhaSenhaSuperSecreta123"
    enc = security.encrypt(test_data)
    dec = security.decrypt(enc)
    print(f"Original: {test_data}")
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {dec}")
    assert test_data == dec
