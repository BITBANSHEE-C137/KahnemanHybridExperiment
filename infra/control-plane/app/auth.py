"""Cloudflare Access JWT validation for the ML Lab Control Plane.

Validates JWTs issued by Cloudflare Access using JWKS fetched from
the team's Cloudflare Access endpoint. Provides a FastAPI dependency
for protecting routes behind Cloudflare Access authentication.
"""

import os
import time
from typing import Any, Optional

import httpx
from fastapi import HTTPException, Request
from jose import jwt, JWTError


class CloudflareAuth:
    """Validates Cloudflare Access JWTs against the team's JWKS endpoint.

    Attributes:
        team_domain: The Cloudflare Access team domain (e.g., "bitbanshee-c137").
        policy_aud: The Application Audience (AUD) tag from the Access policy.
    """

    JWKS_CACHE_TTL = 3600  # 1 hour in seconds

    def __init__(
        self,
        team_domain: Optional[str] = None,
        policy_aud: Optional[str] = None,
    ) -> None:
        """Initializes CloudflareAuth with team domain and policy AUD.

        Args:
            team_domain: Cloudflare Access team domain. Falls back to
                CF_TEAM_DOMAIN env var, then "bitbanshee-c137".
            policy_aud: Cloudflare Access policy AUD tag. Falls back to
                CF_POLICY_AUD env var. Required.

        Raises:
            ValueError: If policy_aud is not provided and CF_POLICY_AUD
                is not set.
        """
        self.team_domain = team_domain or os.environ.get(
            "CF_TEAM_DOMAIN", "bitbanshee-c137"
        )
        self.policy_aud = policy_aud or os.environ.get("CF_POLICY_AUD")
        if not self.policy_aud:
            raise ValueError(
                "CF_POLICY_AUD environment variable is required"
            )

        self._jwks_url = (
            f"https://{self.team_domain}.cloudflareaccess.com"
            f"/cdn-cgi/access/certs"
        )
        self._jwks: Optional[dict[str, Any]] = None
        self._jwks_fetched_at: float = 0.0

    def _fetch_jwks(self) -> dict[str, Any]:
        """Fetches JWKS from the Cloudflare Access certs endpoint.

        Returns:
            The JWKS dict containing signing keys.

        Raises:
            HTTPException: If the JWKS endpoint is unreachable.
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(self._jwks_url)
                resp.raise_for_status()
                self._jwks = resp.json()
                self._jwks_fetched_at = time.time()
                return self._jwks
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch Cloudflare JWKS: {exc}",
            )

    def _get_jwks(self) -> dict[str, Any]:
        """Returns cached JWKS, refreshing if stale or missing.

        Returns:
            The JWKS dict containing signing keys.
        """
        now = time.time()
        if self._jwks is None or (now - self._jwks_fetched_at) > self.JWKS_CACHE_TTL:
            return self._fetch_jwks()
        return self._jwks

    def validate_token(self, token: str) -> dict[str, Any]:
        """Decodes and verifies a Cloudflare Access JWT.

        Args:
            token: The raw JWT string from the Cf-Access-Jwt-Assertion header.

        Returns:
            The decoded claims dict containing at minimum 'email' and 'sub'.

        Raises:
            JWTError: If the token is invalid, expired, or signature fails.
        """
        jwks = self._get_jwks()
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=self.policy_aud,
        )
        return claims

    def get_authenticated_user(self, request: Request) -> dict[str, Any]:
        """FastAPI dependency that extracts and validates the Cloudflare JWT.

        Reads the Cf-Access-Jwt-Assertion header, validates the token,
        and returns the decoded claims.

        Args:
            request: The incoming FastAPI Request object.

        Returns:
            Dict with at least 'email' and 'sub' from the JWT claims.

        Raises:
            HTTPException: 401 if header is missing, 403 if token is invalid.
        """
        token = request.headers.get("Cf-Access-Jwt-Assertion")
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Missing Cloudflare Access token",
            )
        try:
            claims = self.validate_token(token)
            return {"email": claims.get("email"), "sub": claims.get("sub")}
        except JWTError as exc:
            raise HTTPException(
                status_code=403,
                detail=f"Invalid or expired Cloudflare Access token: {exc}",
            )
