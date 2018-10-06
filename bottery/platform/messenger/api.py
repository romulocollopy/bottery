import logging

from bottery.platform.messenger.message import ButtonMessage

logger = logging.getLogger('bottery.messenger')


class MessengerAPI:
    url = 'https://graph.facebook.com/{0}{1}?access_token={2}'

    def __init__(self, token, session, version='v2.6'):
        self.token = token
        self.session = session
        self.version = version

    def make_url(self, method):
        return self.url.format(self.version, method, self.token)

    async def messages(self, response, type='RESPONSE'):
        if isinstance(response.source, ButtonMessage):
            buttons = [
                {'type': b.type, 'title': b.title, 'payload': b.payload}
                for b in response.source.buttons
            ]
            request = {
                'recipient': {
                    'id': response.source.user,
                },
                'message': {
                    'attachment': {
                        'type': 'template',
                        'payload': {
                            'template_type': 'button',
                            'text': response.source.text,
                            'buttons': buttons
                        }
                    }
                },
            }
        else:
            request = {
                'message_type': type,
                'recipient': {
                    'id': response.source.user,
                },
                'message': {
                    'text': response.text,
                },
            }

        url = self.make_url('/me/messages')
        return await self.session.post(url, json=request)
