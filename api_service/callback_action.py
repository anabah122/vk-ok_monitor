from datetime import datetime

from api_service.mixins.wall     import WallMixin
from api_service.mixins.likes    import LikesMixin
from api_service.mixins.members  import MembersMixin
from api_service.mixins.media    import MediaMixin
from api_service.mixins.misc     import MiscMixin
from api_service.mixins.messages import MessagesMixin



class CallbackAction(WallMixin, LikesMixin, MembersMixin, MediaMixin, MiscMixin, MessagesMixin):

    def __init__(self, cache=None):
        self._cache = cache

    def dispatch(self, data: dict):
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