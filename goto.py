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


async def goto(target_x: int, target_y: int):
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
    for product in robot_vacuum_products:
        device = device_by_product_id.get(product.id)
        if not device:
            logger.error(
                "No device found for product %s with id %s", product.name, product.id
            )
            continue

        mqtt_client = RoborockMqttClientV1(
            user_data, DeviceData(device, product.model)
        )
        await mqtt_client.send_command(
            RoborockCommand.APP_GOTO_TARGET, [target_x, target_y]
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send all vacuums to target coordinates."
    )
    parser.add_argument("target_x", type=int, help="Target X coordinate (in mm)")
    parser.add_argument("target_y", type=int, help="Target Y coordinate (in mm)")
    args = parser.parse_args()

    asyncio.run(goto(args.target_x, args.target_y))
