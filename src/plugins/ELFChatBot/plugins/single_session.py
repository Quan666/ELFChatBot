from typing import Dict, Optional

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot.message import run_preprocessor, run_postprocessor, IgnoredException

_running_matcher: Dict[str, int] = {}


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    try:
        session_id = event.get_session_id()
    except:
        session_id = None
    event_id = id(event)
    eid = _running_matcher.get(session_id, None)
    if eid != event_id and eid is not None:
        raise IgnoredException("Annother matcher running")

    _running_matcher[session_id] = event_id


@run_postprocessor
async def _(matcher: Matcher, exception: Optional[Exception], bot: Bot, event: Event, state: T_State):
    try:
        session_id = event.get_session_id()
    except:
        session_id = None
    if session_id in _running_matcher:
        del _running_matcher[session_id]
