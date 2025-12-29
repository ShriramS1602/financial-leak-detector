"""
Crypto utilities for password decryption
Uses RSA encryption for secure password transport from frontend
"""

import os
import base64
import logging
from pathlib import Path
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# Load .env file (support running from different directories)
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Try default locations

logger = logging.getLogger(__name__)

# RSA Key pair for password encryption/decryption
# Keys MUST be set in .env file (single-line format with \n escape sequences)
# Generate new keys using: openssl genrsa -out private_key.pem 2048
#                          openssl rsa -in private_key.pem -pubout -out public_key.pem


def _load_rsa_key_from_env(env_var: str) -> str:
    """Load RSA key from environment variable and convert \n to actual newlines"""
    key = os.getenv(env_var)
    if not key:
        raise ValueError(f"Environment variable {env_var} is not set. Please add it to your .env file.")
    # Convert escaped newlines to actual newlines
    return key.replace("\\n", "\n")


# Load RSA keys from environment variables
RSA_PRIVATE_KEY_PEM = _load_rsa_key_from_env("RSA_PRIVATE_KEY")
RSA_PUBLIC_KEY_PEM = _load_rsa_key_from_env("RSA_PUBLIC_KEY")

# Cached key objects
_private_key = None
_public_key = None


def _get_private_key():
    """Load and cache the RSA private key"""
    global _private_key
    if _private_key is None:
        try:
            _private_key = serialization.load_pem_private_key(
                RSA_PRIVATE_KEY_PEM.encode(),
                password=None,
                backend=default_backend()
            )
        except Exception as e:
            logger.error(f"Failed to load RSA private key: {e}")
            _private_key = None
    return _private_key


def _get_public_key():
    """Load and cache the RSA public key"""
    global _public_key
    if _public_key is None:
        try:
            _public_key = serialization.load_pem_public_key(
                RSA_PUBLIC_KEY_PEM.encode(),
                backend=default_backend()
            )
        except Exception as e:
            logger.error(f"Failed to load RSA public key: {e}")
            _public_key = None
    return _public_key


def generate_rsa_key_pair():
    """
    Generate a new RSA key pair (for initial setup)
    Returns tuple of (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    return private_pem, public_pem


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt a password that was encrypted with the RSA public key on the frontend.
    
    Args:
        encrypted_password: Base64-encoded RSA-OAEP encrypted password
        
    Returns:
        Decrypted plain text password
        
    Raises:
        ValueError: If decryption fails
    """
    # Check if this looks like an encrypted password (long base64 string)
    # RSA 2048 encrypted output is 256 bytes = ~344 base64 chars
    if len(encrypted_password) < 100:
        # Short password - likely not encrypted, return as is
        logger.debug(f"Password appears unencrypted (length: {len(encrypted_password)})")
        return encrypted_password
    
    private_key = _get_private_key()
    
    if private_key is None:
        logger.warning("RSA decryption not available, attempting base64 decode fallback")
        # Fallback to base64 decode if RSA is not configured
        try:
            decoded = base64.b64decode(encrypted_password).decode('utf-8')
            # If decoded is still very long, something is wrong
            if len(decoded) > 72:
                logger.error("Decoded password is too long, RSA key may not be configured correctly")
                raise ValueError("Password decryption failed - RSA key not configured")
            return decoded
        except Exception as e:
            logger.error(f"Base64 decode fallback failed: {e}")
            # If it's not base64 encoded, return as is (plain password)
            return encrypted_password
    
    try:
        # Decode base64 encrypted data
        encrypted_bytes = base64.b64decode(encrypted_password)
        
        logger.debug(f"Attempting RSA decryption of {len(encrypted_bytes)} bytes")
        
        # Decrypt using RSA-OAEP
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        decrypted_str = decrypted.decode('utf-8')
        logger.debug(f"RSA decryption successful, password length: {len(decrypted_str)}")
        return decrypted_str
        
    except Exception as e:
        logger.error(f"RSA decryption failed: {e}")
        # Fallback to base64 decode
        try:
            decoded = base64.b64decode(encrypted_password).decode('utf-8')
            if len(decoded) <= 72:
                return decoded
            logger.error("Fallback base64 decode produced password > 72 bytes")
            raise ValueError(f"Password decryption failed: {e}")
        except Exception as e2:
            logger.error(f"All decryption attempts failed: {e2}")
            # If all else fails, return as is only if it's short enough
            if len(encrypted_password) <= 72:
                return encrypted_password
            raise ValueError(f"Password decryption failed: {e}")


def encrypt_password(password: str) -> str:
    """
    Encrypt a password using RSA (for testing purposes)
    
    Args:
        password: Plain text password
        
    Returns:
        Base64-encoded RSA-OAEP encrypted password
    """
    public_key = _get_public_key()
    
    if public_key is None:
        raise ValueError("RSA public key not available")
    
    encrypted = public_key.encrypt(
        password.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return base64.b64encode(encrypted).decode('utf-8')


def is_password_encrypted(password: str) -> bool:
    """
    Check if a password appears to be RSA encrypted (base64 encoded)
    
    This is a heuristic check - base64 strings with valid RSA encrypted 
    content are typically longer than 200 characters for 2048-bit RSA
    """
    try:
        # RSA 2048 encrypted output is 256 bytes = ~344 base64 chars
        if len(password) > 200:
            decoded = base64.b64decode(password)
            # 2048-bit RSA produces 256-byte output
            return len(decoded) == 256
    except Exception:
        pass
    return False
