import argparse
import asyncio
import base64
import binascii
import logging
import pickle
import os
from typing import Tuple

from roborock import UserData
from roborock.web_api import RoborockApiClient

logger = logging.getLogger(__name__)


USER_DATA_FILE = os.getenv(
    "ROBOROCK_USER_DATA_FILE",
    "user.pkl"
)


def save_user_data(username: str, user_data: UserData) -> None:
    """Save user data after code login."""
    data = pickle.dumps((username, user_data))
    with open(USER_DATA_FILE, "wb") as f:
        f.write(data)
    logger.info("User data saved successfully.")
    b64 = base64.b64encode(data).decode()
    print(
        f"Store the following value as the ROBOROCK_USER_DATA GitHub Actions secret:\n{b64}"
    )


def load_user() -> Tuple[str, UserData]:
    """Load user data from the ROBOROCK_USER_DATA env var (base64) or from file."""
    env_data = os.getenv("ROBOROCK_USER_DATA")
    if env_data:
        try:
            username, user_data = pickle.loads(base64.b64decode(env_data))
            logger.info("User data loaded from environment variable.")
            return username, user_data
        except (binascii.Error, pickle.UnpicklingError, ValueError, TypeError, EOFError) as exc:
            raise ValueError(
                "ROBOROCK_USER_DATA env var is set but could not be decoded. "
                "Please re-run the authenticate workflow."
            ) from exc
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
