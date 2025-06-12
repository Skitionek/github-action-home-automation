import argparse
import asyncio
import logging

from auth import load_user
from roborock import (
    DeviceData,
    HomeDataDevice,
    HomeDataProduct,
    RoborockCategory,
    RoborockCommand,
    UserData,
)
from roborock.version_1_apis import RoborockLocalClientV1, RoborockMqttClientV1
from roborock.web_api import RoborockApiClient

logger = logging.getLogger(__name__)


async def get_local_client(
    user_data: UserData,
    home_data_product: HomeDataProduct,
    home_data_device: HomeDataDevice,
) -> RoborockLocalClientV1:
    """Get a local client for the device."""

    # Create the Mqtt(aka cloud required) Client
    mqtt_client = RoborockMqttClientV1(
        user_data, DeviceData(home_data_device, home_data_product.model)
    )
    networking = await mqtt_client.get_networking()
    if not networking or not networking.ip:
        raise ValueError(
            f"Failed to get networking data for product {home_data_product.name} with id {home_data_product.id}"
        )
    return RoborockLocalClientV1(
        DeviceData(home_data_device, home_data_product.model, networking.ip)
    )


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

        local_client = await get_local_client(user_data, product, device)
        await local_client.send_command(
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
