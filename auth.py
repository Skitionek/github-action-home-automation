import argparse
import asyncio
import logging
import os
from typing import Tuple

import yaml
from roborock import RoborockException, UserData
from roborock.web_api import RoborockApiClient

logger = logging.getLogger(__name__)


def save_user_data(username: str, user_data: UserData) -> None:
    """Print credentials to stdout for manual setup as GitHub Actions secrets."""
    dumped_user_data = yaml.dump(user_data.as_dict(), default_flow_style=False)
    trimmed_user_data = dumped_user_data.rstrip("\n")
    indented_user_data = trimmed_user_data.replace("\n", "\n    ")

    print("\nAdd the following as GitHub Actions secrets:")
    print(f"  ROBOROCK_USERNAME  = {username}")
    print(f"  ROBOROCK_USER_DATA = |")
    print(indented_user_data)


def load_user() -> Tuple[str, UserData]:
    """Load credentials from ROBOROCK_USERNAME and ROBOROCK_USER_DATA env vars."""
    username = os.environ.get("ROBOROCK_USERNAME")
    env_data = os.environ.get("ROBOROCK_USER_DATA")

    if not username:
        raise ValueError("ROBOROCK_USERNAME env var is not set.")
    if not env_data:
        raise ValueError("ROBOROCK_USER_DATA env var is not set.")

    try:
        user_data = UserData.from_dict(yaml.safe_load(env_data))
        logger.info("User data loaded from environment variable.")
        return username, user_data
    except (yaml.YAMLError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "ROBOROCK_USER_DATA env var could not be parsed as YAML. "
            "Expected a YAML mapping with Roborock token fields. "
            "Please re-run auth.py and update the secret."
        ) from exc


async def authenticate_user(
    _web_api: RoborockApiClient, code_or_password: str
) -> UserData:
    """Authenticate user with the provided code."""
    for method in [_web_api.code_login, _web_api.pass_login]:
        try:
            return await method(code_or_password)
        except RoborockException as e:
            logger.debug("Authentication failed with %s: %s", method.__name__, e)
            continue

    logger.error("All authentication methods failed.")
    raise ValueError("Authentication failed. Please check your credentials.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # Try to obtain user data
    parser = argparse.ArgumentParser(description="Roborock authentication")
    parser.add_argument(
        "--username",
        help="Username (email)",
        default=os.environ.get("ROBOROCK_USERNAME"),
    )
    parser.add_argument("code_or_password", help="Code or password")
    args = parser.parse_args()

    logger.info("Starting authentication process for user: %s", args.username)
    logger.debug("Using code_or_password: %s", args.code_or_password)

    web_api = RoborockApiClient(username=args.username)
    user_data = asyncio.run(authenticate_user(web_api, args.code_or_password))
    save_user_data(args.username, user_data)
