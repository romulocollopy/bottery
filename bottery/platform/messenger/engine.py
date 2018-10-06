import asyncio
import logging

from aiohttp import web

from bottery.conf import settings
from bottery.message import Message
from bottery.platform import BaseEngine
from bottery.platform.messenger import MessengerAPI

logger = logging.getLogger('bottery.messenger')


class MessengerEngine(BaseEngine):
    platform = 'messenger'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = MessengerAPI(self.token, session=self.session)

    async def configure(self):
        hostname = getattr(settings, 'HOSTNAME')
        if not hostname:
            raise Exception('Missing HOSTNAME setting')

        self.server.router.add_post('/%s' % self.engine_name, self.webhook)
        self.server.router.add_get('/%s' % self.engine_name,
                                   self.verify_webhook)

    async def verify_webhook(self, request):
        hub_mode = request.query.get('hub.mode')
        verify_token = request.query.get('hub.verify_token')
        secret_key = self.settings.SECRET_KEY

        if hub_mode and verify_token:
            if hub_mode == 'subscribe' and verify_token == secret_key:
                return web.Response(text=request.query['hub.challenge'])

            return web.HTTPForbidden()

    async def webhook(self, request):
        content = await request.json()
        if not content.get('object') == 'page':
            return web.HTTPBadRequest()

        try:
            messages = content['entry'][0]['messaging']
        except KeyError:
            return web.HTTPBadRequest()

        messages = content['entry'][0]['messaging']
        updates = [self.message_handler(message) for message in messages]
        await asyncio.gather(*updates)
        return web.Response(text='EVENT_RECEIVED')

    def build_message(self, data):
        '''
        Return a Message instance according to the data received from
        Facebook Messenger API.
        '''
        if not data or 'text' not in data.get('message', []):
            return None

        if 'postback' in data:
            data['message'] = data['postback']
            data['message']['text'] = data['postback']['payload']
            data['message']['mid'] = data['postback']['title']

        return Message(
            id=data['message'].get('mid'),
            platform=self.platform,
            text=data['message'].get('text'),
            user=data['sender']['id'],
            timestamp=data['timestamp'],
            raw=data,
            chat=None,  # TODO: Refactor build_messages and Message class
        )

    async def send_response(self, response):
        await self.api.messages(response.source.user, response.text)
