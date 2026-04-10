import time, os
from dotenv import load_dotenv

load_dotenv()


CONFIRMATION_CODE_VK = os.environ["CONFIRMATION_CODE_VK"]
SECRET_KEY_VK_GROUP  = os.environ["SECRET_KEY_VK_GROUP"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = os.environ["DB_NAME"]
DB_PATH  = os.path.join(BASE_DIR, "DB", DB_NAME)

AUTH_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth_service", 'users.db') 