"""
Pika Network API wrapper with async HTTP requests, caching, and error handling.
"""

import logging
import time
from typing import Any, Optional

import aiohttp

from bot.config import Config

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when the Pika Network API returns an error."""

    def __init__(self, message: str, status_code: int = 0):
        self.status_code = status_code
        super().__init__(message)


class PlayerNotFoundError(APIError):
    """Raised when a player is not found."""
    pass


class GuildNotFoundError(APIError):
    """Raised when a guild/clan is not found."""
    pass


class RateLimitError(APIError):
    """Raised when rate limited by the API."""
    pass


class _Cache:
    """Simple TTL cache for API responses."""

    def __init__(self, ttl: int = 60):
        self._store: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            timestamp, value = self._store[key]
            if time.time() - timestamp < self._ttl:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        self._store.clear()


class PikaAPI:
    """Async wrapper for the Pika Network Stats API."""

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache = _Cache(ttl=120)  # 2-minute cache

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": "PikaStatsBot/2.0"},
            )
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, url: str, use_cache: bool = True) -> Any:
        """Make an async GET request with caching and error handling."""
        if use_cache:
            cached = self._cache.get(url)
            if cached is not None:
                logger.debug("Cache hit: %s", url)
                return cached

        session = await self._get_session()
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if use_cache:
                        self._cache.set(url, data)
                    return data
                elif response.status == 404:
                    return None
                elif response.status == 429:
                    raise RateLimitError(
                        "Rate limited by Pika Network API. Please try again later.",
                        status_code=429,
                    )
                else:
                    raise APIError(
                        f"API returned status {response.status}",
                        status_code=response.status,
                    )
        except aiohttp.ClientError as e:
            logger.error("HTTP request failed: %s", e)
            raise APIError(f"Failed to connect to Pika Network API: {e}")

    # ── Player Profile ──────────────────────────────────────────────

    async def get_profile(self, player_name: str) -> dict:
        """
        Fetch a player's profile information.

        Returns dict with keys: username, rank, level, percentage, experience,
        lastSeen, friends, clan, discord_verified, email_verified, etc.
        """
        url = f"{Config.PIKA_API_BASE}/profile/{player_name}"
        data = await self._request(url)
        if data is None:
            raise PlayerNotFoundError(f"Player '{player_name}' not found.")
        return data

    # ── Player Stats (Leaderboard) ──────────────────────────────────

    async def get_stats(
        self,
        player_name: str,
        game_type: str,
        interval: str = "total",
        mode: str = "ALL_MODES",
    ) -> dict:
        """
        Fetch a player's game statistics.

        Args:
            player_name: The player's username.
            game_type: Game type (bedwars, skywars, unrankedpractice, etc.).
            interval: Time interval (total, monthly, weekly, daily).
            mode: Game mode (ALL_MODES, solo, doubles, etc.).

        Returns:
            Dict mapping stat names to their metadata (total, rank, etc.).
        """
        url = (
            f"{Config.PIKA_API_BASE}/profile/{player_name}/leaderboard"
            f"?type={game_type}&interval={interval}&mode={mode}"
        )
        data = await self._request(url)
        if data is None:
            raise PlayerNotFoundError(f"Player '{player_name}' not found.")
        return data

    # ── Guild / Clan ────────────────────────────────────────────────

    async def get_guild(self, guild_name: str) -> dict:
        """
        Fetch guild/clan information.

        Returns dict with keys: name, tag, owner, members, leveling,
        creationTime, etc.
        """
        url = f"{Config.PIKA_API_BASE}/clans/{guild_name}"
        data = await self._request(url)
        if data is None:
            raise GuildNotFoundError(f"Guild '{guild_name}' not found.")
        return data

    # ── Minecraft UUID (for skin rendering) ─────────────────────────

    async def get_minecraft_uuid(self, player_name: str) -> Optional[str]:
        """
        Resolve a Minecraft username to a UUID using Minetools API.
        Returns the UUID string or None if not found.
        """
        url = f"{Config.MINETOOLS_API}/{player_name}"
        try:
            data = await self._request(url, use_cache=True)
            if data and data.get("id"):
                return data["id"]
        except APIError:
            pass
        return None

    # ── Skin / Avatar URLs ──────────────────────────────────────────

    @staticmethod
    def get_avatar_url(uuid: str, size: int = 128) -> str:
        """Get the player's face avatar URL from Crafatar."""
        return f"{Config.CRAFATAR_BASE}/avatars/{uuid}?size={size}&overlay"

    @staticmethod
    def get_head_url(uuid: str, size: int = 128) -> str:
        """Get the player's 3D head render URL from Crafatar."""
        return f"{Config.CRAFATAR_BASE}/renders/head/{uuid}?scale=4&overlay"

    @staticmethod
    def get_body_url(uuid: str, size: int = 128) -> str:
        """Get the player's full body render URL from Crafatar."""
        return f"{Config.CRAFATAR_BASE}/renders/body/{uuid}?scale=4&overlay"

    @staticmethod
    def get_skin_url(uuid: str) -> str:
        """Get the player's raw skin texture URL from Crafatar."""
        return f"{Config.CRAFATAR_BASE}/skins/{uuid}"

    # ── Utility ─────────────────────────────────────────────────────

    @staticmethod
    def calculate_ratio(numerator: float, denominator: float) -> str:
        """Calculate a ratio (e.g., KDR, WLR) and return formatted string."""
        if denominator == 0:
            return f"{numerator:.2f}" if numerator > 0 else "0.00"
        return f"{numerator / denominator:.2f}"

    @staticmethod
    def get_stat_value(stats: dict, stat_name: str) -> int:
        """Safely extract a stat's total value from the API response."""
        stat = stats.get(stat_name, {})
        metadata = stat.get("metadata", {})
        return int(metadata.get("total", 0))

    @staticmethod
    def get_stat_rank(stats: dict, stat_name: str) -> str:
        """Safely extract a stat's rank from the API response."""
        stat = stats.get(stat_name, {})
        metadata = stat.get("metadata", {})
        rank = metadata.get("rank", None)
        return f"#{rank}" if rank else "N/A"


# Global API instance
pika_api = PikaAPI()
