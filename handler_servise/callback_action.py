from datetime import datetime

from handler_servise.mixins.wall     import WallMixin
from handler_servise.mixins.likes    import LikesMixin
from handler_servise.mixins.members  import MembersMixin
from handler_servise.mixins.media    import MediaMixin
from handler_servise.mixins.misc     import MiscMixin
from handler_servise.mixins.messages import MessagesMixin

import _G


class CallbackAction(WallMixin, LikesMixin, MembersMixin, MediaMixin, MiscMixin, MessagesMixin):

    def __init__(self, cache=None):
        self._cache = cache

    def validate(self, data: dict):
        if not data:
            return "bad request"
        if data.get("type") == "confirmation":
            return _G.CONFIRMATION_CODE_VK
        if _G.SECRET_KEY_VK_GROUP and data.get("secret") != _G.SECRET_KEY_VK_GROUP:
            return "forbidden"
        return False

    def dispatch(self, data: dict):
        is_invalid = self.validate(data)
        if is_invalid:
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
                handler(obj, group_id)
            except Exception as e:
                print(f"  ⚠️  Ошибка в {handler_name}: {e}")
                print(f"      object: {obj}")
        else:
            print(f"  ❓ Неизвестное событие: {event_type}")
            print(f"     object: {obj}")

        if self._cache and group_id:
            self._cache.set_group_invalid(group_id)

        return "ok"