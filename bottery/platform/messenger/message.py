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

    @buttons.validator
    def validate_buttons(self, attribute, value):
        if len(value) > 3:
            docs_url = ("https://developers.facebook.com/docs/"
                        "messenger-platform/send-messages/template/generic")
            raise ValueError("Facebook only allows up to three buttons. "
                             "Check {} for details".format(docs_url))

    @property
    def datetime(self):
        return datetime.utcfromtimestamp(self.timestamp)
