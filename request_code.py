import argparse
import asyncio
import logging

from roborock.web_api import RoborockApiClient

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Request code for Roborock account.")
    parser.add_argument("username", help="Roborock account username")
    args = parser.parse_args()

    web_api = RoborockApiClient(username=args.username)
    asyncio.run(web_api.request_code())
