import os

from dotenv import load_dotenv

load_dotenv()


MATRIX_USER = os.environ["MATRIX_USER"]
MATRIX_PASSWORD = os.environ["MATRIX_PASSWORD"]
MATRIX_ROOM_ID = os.environ["MATRIX_ROOM_ID"]
MATRIX_SERVER = os.getenv("MATRIX_SERVER", "https://matrix.org")

CHECK_DELAY = int(os.getenv("CHECK_DELAY", 120))
CAPY_LIFE_LINK = os.getenv("CAPY_LIFE_LINK", "https://capy.life")
CAPY_API_LINK = os.getenv("CAPY_API_LINK", "http://localhost/api/")

MONGO_HOST = os.getenv("MONGO_IP", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "neocapy")
