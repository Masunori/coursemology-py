import base64
import hashlib
import os
import re
import secrets
import time
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from pydantic import BaseModel, Field
from requests.auth import AuthBase
from requests.models import PreparedRequest, Response


class OIDCTokens(BaseModel):
    """
    A Pydantic model to store and manage OIDC tokens with strong typing.
    Includes logic for expiry calculation.
    """

    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str
    scope: str
    obtained_at: float = Field(default_factory=time.time)

    @property
    def expires_at(self) -> float:
        """
        Calculates the token's expiry timestamp with a 60-second safety margin.
        """
        return self.obtained_at + self.expires_in - 60

    @property
    def is_expired(self) -> bool:
        """Checks if the access token has expired."""
        return time.time() >= self.expires_at


def _b64url_no_padding(b: bytes) -> str:
    """Encodes bytes in URL-safe Base64 without padding."""
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def _make_pkce_pair() -> tuple[str, str]:
    """Generates a PKCE code verifier and challenge pair."""
    verifier = _b64url_no_padding(os.urandom(64))
    challenge = _b64url_no_padding(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


def _extract_login_action(html: str) -> str:
    """Extracts the Keycloak login action URL from the login page HTML."""
    m = re.search(r'"loginAction"\s*:\s*"([^"]+)"', html)
    if not m:
        m = re.search(r'loginAction"\s*:\s*(https?://[^",]+)', html)
    if not m:
        raise RuntimeError("Unable to find Keycloak loginAction URL in the login page.")
    return m.group(1).replace("\\/", "/")


class OIDCBearerAuth(AuthBase):
    """
    A requests AuthBase class that injects the Bearer token and handles
    automatic token refreshing before a request is sent.
    """

    def __init__(self, client_id: str, tokens: OIDCTokens, token_endpoint: str):
        self.client_id = client_id
        self.tokens = tokens
        self.token_endpoint = token_endpoint

    def refresh_tokens(self) -> None:
        """Refreshes the access token using the refresh token."""
        print("Access token expired or invalid. Refreshing...")
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.tokens.refresh_token,
        }
        r = requests.post(self.token_endpoint, data=data, timeout=30)
        r.raise_for_status()

        new_token_data = r.json()
        self.tokens = OIDCTokens.model_validate(new_token_data)
        print("Token refreshed successfully.")

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        if self.tokens.is_expired:
            self.refresh_tokens()

        r.headers["Authorization"] = f"Bearer {self.tokens.access_token}"
        return r


class CoursemologySession(requests.Session):
    """
    A custom requests.Session that automatically handles 401 Unauthorized
    errors by refreshing the OIDC token and retrying the request once.
    """

    def request(self, *args: Any, **kwargs: Any) -> Response:
        """
        Overrides the default request method to add 401 retry logic.
        Uses a generic signature to safely wrap the parent method.
        """
        # The initial request is made by the parent class.
        # self.auth (OIDCBearerAuth) is called automatically before the request.
        response = super().request(*args, **kwargs)

        if response.status_code == 401:
            print("Request failed with 401. Retrying after token refresh...")
            # The auth handler must be our custom one.
            if isinstance(self.auth, OIDCBearerAuth):
                self.auth.refresh_tokens()
                # Retry the request. The parent's request method will again
                # call our auth handler, which now has a fresh token.
                response = super().request(*args, **kwargs)

        return response


class CoursemologyAuthenticator:
    """
    Handles the OIDC Authorization Code + PKCE flow for Coursemology to
    obtain a fully configured and authenticated requests.Session.
    """

    def __init__(
        self,
        issuer: str = "https://auth.coursemology.org/realms/coursemology",
        client_id: str = "2bb4ea97-c017-4613-91fb-a1219aef3935",
        redirect_uri: str = "https://coursemology.org",
        scope: str = "openid email user_id",
    ):
        self.issuer = issuer
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.auth_endpoint = f"{issuer}/protocol/openid-connect/auth"
        self.token_endpoint = f"{issuer}/protocol/openid-connect/token"

    def _exchange_code_for_tokens(self, session: requests.Session, code: str, code_verifier: str) -> OIDCTokens:
        """Exchanges the authorization code for access and refresh tokens."""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "code_verifier": code_verifier,
        }
        r = session.post(self.token_endpoint, data=data, timeout=30)
        r.raise_for_status()
        return OIDCTokens.model_validate(r.json())

    def get_api_session(self, username: str, password: str) -> CoursemologySession:
        """
        Performs the full login flow and returns a CoursemologySession
        configured with automatic token management.
        """
        login_session = requests.Session()
        login_session.headers.update({"User-Agent": "coursemology-py/1.0"})

        code_verifier, code_challenge = _make_pkce_pair()
        state = _b64url_no_padding(secrets.token_bytes(16))

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{self.auth_endpoint}?{urlencode(params)}"

        # 1. Get the Keycloak login page
        r = login_session.get(auth_url, allow_redirects=True, timeout=30)
        r.raise_for_status()

        # 2. Extract loginAction and submit credentials to get the authorization code
        login_action = _extract_login_action(r.text)
        form = {"username": username, "password": password, "credentialId": ""}
        r = login_session.post(login_action, data=form, allow_redirects=False, timeout=30)

        if r.status_code not in (302, 303):
            if '"loginAction"' in r.text:
                raise RuntimeError("Login failed: Invalid credentials or MFA/challenge required.")
            r.raise_for_status()
            raise RuntimeError(f"Unexpected status after login POST: {r.status_code}")

        location = r.headers.get("Location", "")
        if not location or not location.startswith(self.redirect_uri):
            raise RuntimeError(f"Expected redirect to {self.redirect_uri}, got: {location}")

        parsed_url = urlparse(location)
        query_params = parse_qs(parsed_url.query)
        code = query_params.get("code", [None])[0]
        returned_state = query_params.get("state", [None])[0]

        if not code or returned_state != state:
            raise RuntimeError("Missing code or state mismatch in Keycloak redirect.")

        # 3. Exchange authorization code for tokens
        tokens = self._exchange_code_for_tokens(login_session, code, code_verifier)

        # 4. Create and configure the final API session using our custom class
        auth_handler = OIDCBearerAuth(self.client_id, tokens, self.token_endpoint)
        api_session = CoursemologySession()
        api_session.auth = auth_handler
        api_session.headers.update({"User-Agent": "coursemology-py/1.0"})

        # 5. Fetch the CSRF token from the dedicated endpoint
        csrf_url = f"{self.redirect_uri}/csrf_token"
        csrf_response = api_session.get(csrf_url, params={"format": "json"})
        csrf_response.raise_for_status()
        api_session._csrf_token = csrf_response.json()["csrfToken"]  # type: ignore

        return api_session
