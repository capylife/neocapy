import asyncio

from neocapy import NeoCapy


if __name__ == "__main__":
    neo = NeoCapy()
    try:
        asyncio.run(neo.run())
    except KeyboardInterrupt:
        asyncio.run(neo.close())
