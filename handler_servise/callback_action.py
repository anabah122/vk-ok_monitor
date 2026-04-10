from datetime import datetime

from handler_servise.mixins.wall    import WallMixin
from handler_servise.mixins.likes   import LikesMixin
from handler_servise.mixins.members import MembersMixin
from handler_servise.mixins.media   import MediaMixin
from handler_servise.mixins.misc    import MiscMixin
from handler_servise.mixins.messages import MessagesMixin

import time
import _G 


class CallbackAction(WallMixin, LikesMixin, MembersMixin, MediaMixin, MiscMixin, MessagesMixin):
    """
    Диспетчер событий VK Callback API.
    Каждое событие маппится на метод on_<event_type>.
    Если метод не реализован — логируется как неизвестное событие.
    """
    def validate(self, data: dict):
        if not data:
            return "bad request"

        if data.get("type") == "confirmation":
            return _G.CONFIRMATION_CODE_VK

        if _G.SECRET_KEY and data.get("secret") != _G.SECRET_KEY_VK_GROUP:
            return "forbidden"
        
        return None


    def dispatch(self, data: dict):

        is_invalid = self.validate(data)
        if is_invalid : 
            return is_invalid

        event_type = data.get("type")
        obj        = data.get("object", {})
        group_id   = data.get("group_id")
        ts         = datetime.now().strftime("%H:%M:%S")

        print(f"\n[{ts}] EVENT: {event_type} | group={group_id}")

        handler_name = f"on_{event_type}"
        handler = getattr(self, handler_name, None)

        if handler:
            try:
                handler(obj)
            except Exception as e:
                print(f"  ⚠️  Ошибка в {handler_name}: {e}")
                print(f"      object: {obj}")
        else:
            print(f"  ❓ Неизвестное событие: {event_type}")
            print(f"     object: {obj}")

        _G.LAST_ACTION_TIMESTAMP = time.time()
        return "ok" 


