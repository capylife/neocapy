import asyncio
import logging
import mimetypes

from aiohttp import ClientSession
from nio import AsyncClient, LoginResponse
from motor.motor_asyncio import AsyncIOMotorClient
from sys import stdout
from json import JSONDecodeError
from io import BytesIO

from .env import (
    MATRIX_SERVER, MATRIX_USER, MATRIX_PASSWORD,
    CHECK_DELAY, MONGO_HOST, MONGO_PORT, MONGO_DB,
    CAPY_API_LINK, MATRIX_ROOM_ID, CAPY_LIFE_LINK
)

logger = logging.getLogger("neocapy")
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stdout)
logger.addHandler(consoleHandler)


class NeoCapy:
    async def run(self) -> None:
        self.__client = AsyncClient(
            MATRIX_SERVER, MATRIX_USER,
        )
        self.__http = ClientSession()
        self.__mongo = AsyncIOMotorClient(
            MONGO_HOST, MONGO_PORT
        )
        self.__collection = self.__mongo[MONGO_DB]

        login = await self.__client.login(MATRIX_PASSWORD)

        if not isinstance(login, LoginResponse):
            logger.info("Login details invalid!")
            await self.close()
            return

        while True:
            logger.info(f"Waiting {CHECK_DELAY} seconds till next check.")
            await asyncio.sleep(CHECK_DELAY)

            async with self.__http.get(CAPY_API_LINK) as resp:
                if resp.status != 200:
                    logger.warn((
                        f"HTTP Request to \"{CAPY_API_LINK}\""
                        f" gave status code {resp.status}"
                    ))
                    continue

                try:
                    json = await resp.json()
                except JSONDecodeError as error:
                    logger.warn(error)
                    continue

                record = await self.__collection.used.find_one({
                    "_id": json["_id"]
                })
                if record:
                    continue

                async with self.__http.get(json["image"]) as img_resp:
                    if resp.status != 200:
                        logger.warn((
                            f"HTTP Request to \"{json['image']}\""
                            f" gave status code {img_resp.status}"
                        ))
                        continue

                    file_ext = mimetypes.guess_extension(
                        img_resp.headers["Content-Type"]
                    )
                    if not file_ext:
                        logger.warn((
                            "Unable to determine file ext from"
                            "Content type "
                            f"'{img_resp.headers['Content-Type']}'"
                        ))
                        continue

                    image = await img_resp.read()
                    image_size = len(image)

                    upload, _ = await self.__client.upload(
                        BytesIO(image),
                        content_type=img_resp.headers["Content-Type"],
                        filesize=image_size,
                        filename=json["_id"] + file_ext
                    )

                    await self.__client.room_send(
                        room_id=MATRIX_ROOM_ID,
                        message_type="m.room.message",
                        content={
                            "body": f"New capybara named {json['name']}",
                            "info": {
                                "size": image_size,
                                "mimetype": img_resp.headers["Content-Type"],
                            },
                            "msgtype": "m.image",
                            "url": upload.content_uri,
                        }
                    )
                    await self.__client.room_send(
                        room_id=MATRIX_ROOM_ID,
                        message_type="m.room.message",
                        content={
                            "msgtype": "m.text",
                            "body": (
                                f"Meet {json['name']}!\n"
                                f"Submit a Capybara at {CAPY_LIFE_LINK}"
                            )
                        },
                    )

                    await self.__collection.used.insert_one({
                        "_id": json["_id"]
                    })

                    logger.info(f"Posted {json['name']} to {MATRIX_ROOM_ID}!")

    async def close(self) -> None:
        await self.__client.close()
        await self.__http.close()
