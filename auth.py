import argparse
import asyncio
import logging
import pickle
from typing import Tuple

from roborock import UserData
from roborock.web_api import RoborockApiClient

logger = logging.getLogger(__name__)


USER_DATA_FILE = "user.pkl"


def save_user_data(username: str, user_data: UserData) -> None:
    """Save user data after code login."""
    pickle.dump((username, user_data), open(USER_DATA_FILE, "wb"))
    logger.info("User data saved successfully.")


def load_user() -> Tuple[str, UserData]:
    """Load user data from file."""
    try:
        username, user_data = pickle.load(open(USER_DATA_FILE, "rb"))
        logger.info("User data loaded successfully.")
        return username, user_data
    except (IOError, ValueError, EOFError) as exc:
        raise ValueError(
            "User data not found or corrupted. Please login again."
        ) from exc


async def authenticate_user(
    _web_api: RoborockApiClient, code_or_password: str
) -> UserData:
    """Authenticate user with the provided code."""
    for method in [_web_api.code_login, _web_api.pass_login]:
        try:
            return await method(code_or_password)
        except Exception as e:
            logger.debug("Authentication failed with %s: %s", method.__name__, e)
            continue

    logger.error("All authentication methods failed.")
    raise ValueError("Authentication failed. Please check your credentials.")


if __name__ == "__main__":
    # Try to obtain user data
    parser = argparse.ArgumentParser(description="Roborock authentication")
    parser.add_argument("username", help="Username (email)")
    parser.add_argument("code_or_password", help="Code or password")
    args = parser.parse_args()

    web_api = RoborockApiClient(username=args.username)
    user_data = asyncio.run(authenticate_user(web_api, args.code_or_password))
    save_user_data(args.username, user_data)
