import time, os
from dotenv import load_dotenv

load_dotenv()

CONFIRMATION_CODE_VK = os.environ["CONFIRMATION_CODE_VK"]
SECRET_KEY_VK_GROUP  = os.environ["SECRET_KEY_VK_GROUP"]

LAST_ACTION_TIMESTAMP = time.time()
DB_PATH = "DB/db.db"