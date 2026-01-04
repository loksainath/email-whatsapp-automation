import os
from cryptography.fernet import Fernet

# -------------------------------------------------
# Load encryption key from environment
# -------------------------------------------------
KEY = os.environ.get("ENCRYPTION_KEY")

if not KEY:
    raise RuntimeError(
        "❌ ENCRYPTION_KEY not found. "
        "Please set it in the .env file before starting the application."
    )

# Remove accidental whitespace/newlines
KEY = KEY.strip()

try:
    cipher = Fernet(KEY.encode())
except Exception as e:
    raise RuntimeError(
        "❌ Invalid ENCRYPTION_KEY. "
        "Ensure it is a valid Fernet key."
    ) from e


# -------------------------------------------------
# Encryption helpers
# -------------------------------------------------
def encrypt(text: str) -> str:
    """
    Encrypt sensitive text (e.g., Gmail App Password)
    """
    return cipher.encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    """
    Decrypt previously encrypted text
    """
    return cipher.decrypt(token.encode()).decode()
