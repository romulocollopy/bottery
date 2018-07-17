import attr
from bottery.message import Message


@attr.s
class Button:
    type = attr.ib()
    title = attr.ib()
    payload = attr.ib()


@attr.s
class ButtonMessage(Message):
    buttons = attr.ib(factory=list)

    @property
    def datetime(self):
        return datetime.utcfromtimestamp(self.timestamp)
