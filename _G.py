import time, os
from dotenv import load_dotenv

load_dotenv()


CONFIRMATION_CODE_VK = os.environ["CONFIRMATION_CODE_VK"]
SECRET_KEY_VK_GROUP  = os.environ["SECRET_KEY_VK_GROUP"]

LAST_ACTION_TIMESTAMP = time.time()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "DB", "db.db")

DB_NAME = os.environ.get("DB_NAME", "db.db")
DB_PATH = os.path.join(BASE_DIR, "DB", DB_NAME)