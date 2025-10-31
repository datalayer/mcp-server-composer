"""
Authentication middleware for MCP Server Composer.

This module provides authentication mechanisms to secure access to MCP servers
and tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

import hashlib
import hmac
import secrets


class AuthType(str, Enum):
    """Types of authentication methods."""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    MTLS = "mtls"
    NONE = "none"


@dataclass
class AuthContext:
    """
    Authentication context for a request.
    
    Contains information about the authenticated user/client.
    """
    user_id: str
    auth_type: AuthType
    token: Optional[str] = None
    scopes: list[str] = None
    metadata: Dict[str, Any] = None
    authenticated_at: datetime = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.scopes is None:
            self.scopes = []
        if self.metadata is None:
            self.metadata = {}
        if self.authenticated_at is None:
            self.authenticated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if the authentication context has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def has_scope(self, scope: str) -> bool:
        """Check if the context has a specific scope."""
        return scope in self.scopes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "auth_type": self.auth_type.value,
            "token": self.token,
            "scopes": self.scopes,
            "metadata": self.metadata,
            "authenticated_at": self.authenticated_at.isoformat() if self.authenticated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""
    pass


class ExpiredTokenError(AuthenticationError):
    """Raised when a token has expired."""
    pass


class InsufficientScopesError(AuthenticationError):
    """Raised when required scopes are missing."""
    pass


class Authenticator(ABC):
    """
    Abstract base class for authentication mechanisms.
    
    All authentication implementations should inherit from this class.
    """
    
    def __init__(self, auth_type: AuthType):
        """
        Initialize authenticator.
        
        Args:
            auth_type: Type of authentication this authenticator provides.
        """
        self.auth_type = auth_type
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthContext:
        """
        Authenticate a request using provided credentials.
        
        Args:
            credentials: Dictionary containing authentication credentials.
                Format depends on the authentication type.
        
        Returns:
            AuthContext if authentication succeeds.
        
        Raises:
            AuthenticationError: If authentication fails.
        """
        pass
    
    @abstractmethod
    async def validate(self, context: AuthContext) -> bool:
        """
        Validate an existing authentication context.
        
        Args:
            context: Authentication context to validate.
        
        Returns:
            True if context is still valid, False otherwise.
        """
        pass
    
    async def refresh(self, context: AuthContext) -> AuthContext:
        """
        Refresh an authentication context (if supported).
        
        Args:
            context: Existing authentication context.
        
        Returns:
            New authentication context with extended expiry.
        
        Raises:
            NotImplementedError: If refresh is not supported.
        """
        raise NotImplementedError(f"Refresh not supported for {self.auth_type}")


class APIKeyAuthenticator(Authenticator):
    """
    API Key authentication.
    
    Simple authentication using static API keys.
    """
    
    def __init__(self, api_keys: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize API key authenticator.
        
        Args:
            api_keys: Dictionary mapping API keys to user information.
                Format: {
                    "api_key_hash": {
                        "user_id": "user123",
                        "scopes": ["read", "write"],
                        "metadata": {}
                    }
                }
        """
        super().__init__(AuthType.API_KEY)
        self.api_keys = api_keys or {}
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            api_key: Plain text API key.
        
        Returns:
            Hashed API key.
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a new secure API key.
        
        Returns:
            New API key string.
        """
        return secrets.token_urlsafe(32)
    
    def add_api_key(
        self,
        api_key: str,
        user_id: str,
        scopes: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a new API key.
        
        Args:
            api_key: The API key to add.
            user_id: User ID associated with this key.
            scopes: List of scopes this key has access to.
            metadata: Additional metadata.
        
        Returns:
            Hash of the API key.
        """
        key_hash = self.hash_api_key(api_key)
        self.api_keys[key_hash] = {
            "user_id": user_id,
            "scopes": scopes or [],
            "metadata": metadata or {}
        }
        return key_hash
    
    def remove_api_key(self, api_key: str) -> bool:
        """
        Remove an API key.
        
        Args:
            api_key: The API key to remove.
        
        Returns:
            True if key was removed, False if not found.
        """
        key_hash = self.hash_api_key(api_key)
        if key_hash in self.api_keys:
            del self.api_keys[key_hash]
            return True
        return False
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthContext:
        """
        Authenticate using an API key.
        
        Args:
            credentials: Must contain "api_key" field.
        
        Returns:
            AuthContext for the authenticated user.
        
        Raises:
            InvalidCredentialsError: If API key is invalid.
        """
        api_key = credentials.get("api_key")
        if not api_key:
            raise InvalidCredentialsError("API key not provided")
        
        key_hash = self.hash_api_key(api_key)
        key_info = self.api_keys.get(key_hash)
        
        if not key_info:
            raise InvalidCredentialsError("Invalid API key")
        
        return AuthContext(
            user_id=key_info["user_id"],
            auth_type=AuthType.API_KEY,
            token=api_key,
            scopes=key_info["scopes"],
            metadata=key_info["metadata"],
        )
    
    async def validate(self, context: AuthContext) -> bool:
        """
        Validate an API key authentication context.
        
        Args:
            context: Authentication context to validate.
        
        Returns:
            True if valid, False otherwise.
        """
        if context.auth_type != AuthType.API_KEY:
            return False
        
        if not context.token:
            return False
        
        key_hash = self.hash_api_key(context.token)
        return key_hash in self.api_keys


class NoAuthenticator(Authenticator):
    """
    No authentication (allow all).
    
    Useful for development or internal-only deployments.
    """
    
    def __init__(self):
        """Initialize no-auth authenticator."""
        super().__init__(AuthType.NONE)
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthContext:
        """
        Allow any request without authentication.
        
        Args:
            credentials: Ignored.
        
        Returns:
            AuthContext with anonymous user.
        """
        return AuthContext(
            user_id="anonymous",
            auth_type=AuthType.NONE,
            scopes=["*"],  # All scopes
        )
    
    async def validate(self, context: AuthContext) -> bool:
        """
        Always return True (no validation needed).
        
        Args:
            context: Ignored.
        
        Returns:
            Always True.
        """
        return True


def create_authenticator(auth_type: AuthType, **kwargs) -> Authenticator:
    """
    Factory function to create an authenticator.
    
    Args:
        auth_type: Type of authenticator to create.
        **kwargs: Additional arguments for the authenticator.
    
    Returns:
        Authenticator instance.
    
    Raises:
        ValueError: If auth_type is not supported.
    """
    if auth_type == AuthType.API_KEY:
        return APIKeyAuthenticator(api_keys=kwargs.get("api_keys"))
    elif auth_type == AuthType.NONE:
        return NoAuthenticator()
    else:
        raise ValueError(f"Unsupported auth type: {auth_type}")
