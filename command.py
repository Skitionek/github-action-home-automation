import argparse
import asyncio
import logging

from auth import load_user
from roborock import (
    DeviceData,
    RoborockCategory,
    RoborockCommand,
)
from roborock.version_1_apis import RoborockMqttClientV1
from roborock.web_api import RoborockApiClient

logger = logging.getLogger(__name__)


def parse_command(value: str) -> RoborockCommand:
    """Convert CLI command text to a RoborockCommand enum member."""
    normalized = value.upper()
    try:
        return RoborockCommand[normalized]
    except KeyError as exc:
        valid = ", ".join(cmd.name for cmd in RoborockCommand)
        raise argparse.ArgumentTypeError(
            f"Invalid command '{value}'. Valid commands: {valid}"
        ) from exc


async def broadcast_command(cmd: RoborockCommand, params: list):
    username, user_data = load_user()

    web_api = RoborockApiClient(username=username)

    # Get home data
    home_data = await web_api.get_home_data_v2(user_data)

    # Get all robotic vacuums:
    robot_vacuum_products = [
        product
        for product in home_data.products
        if product.category == RoborockCategory.VACUUM
    ]

    # Prep mapping products to device data:
    device_by_product_id = {
        device.product_id: device for device in home_data.get_all_devices()
    }

    # Do same for all devices:
    failed = []
    for product in robot_vacuum_products:
        device = device_by_product_id.get(product.id)
        if not device:
            logger.error(
                "No device found for product %s with id %s", product.name, product.id
            )
            failed.append(product.name)
            continue

        mqtt_client = RoborockMqttClientV1(
            user_data, DeviceData(device, product.model)
        )
        try:
            yield await mqtt_client.send_command(cmd, params)
        except Exception:
            logger.exception("Failed to send command to device %s", product.name)
            failed.append(product.name)
        finally:
            await mqtt_client.async_disconnect()

    if failed:
        raise RuntimeError(f"Command failed for devices: {', '.join(failed)}")

async def command(cmd: RoborockCommand, params: list):
    async for r in broadcast_command(cmd, params):
        logger.debug("Command result: %s", r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Command to all vacuums"
    )
    parser.add_argument("command", type=parse_command, help="Command to send (e.g. APP_GOTO_TARGET)")
    parser.add_argument("params", nargs="*", help="Command parameters (e.g. target_x target_y)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    asyncio.run(command(args.command, args.params))
    