from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.config import config


class Security:
    """
    Utility class for password hashing and JWT token operations.
    """

    def __init__(self):
        # Initialize password context with Argon2
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        Hashes a plain text password using the Argon2 hashing algorithm.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The argon2 hashed password.
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain text password against a stored hashed password.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to verify against.

        Returns:
            bool: True if password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_jwt_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a new JWT access token.

        Args:
            data (Dict[str, Any]): The payload data to encode in the token.
            expires_delta (Optional[timedelta]): Optional expiration delta.

        Returns:
            str: The encoded JWT token string.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            config.SECRET_KEY, 
            algorithm=config.ALGORITHM
        )
        
        return encoded_jwt

    def decode_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodes a JWT token and returns its payload if valid.

        Args:
            token (str): The JWT token string to decode.

        Returns:
            Optional[Dict[str, Any]]: The decoded payload if valid, None otherwise.
        """
        try:
            payload = jwt.decode(
                token, 
                config.SECRET_KEY, 
                algorithms=[config.ALGORITHM]
            )
            return payload
        except JWTError:
            return None


def get_security() -> Security:
    """
    Dependency function to provide a Security instance.
    
    Returns:
        Security: An instance of the Security class.
    """
    return Security()
