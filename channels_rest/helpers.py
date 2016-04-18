from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.core.urlresolvers import RegexURLResolver
from django.http.request import HttpRequest
from django.utils import six
from django.utils.encoding import force_text
from django.utils.module_loading import import_string

import logging
import json


logger = logging.getLogger(__name__)


class ChannelRestRequest(HttpRequest):
    def __init__(self, message, method="GET"):
        super(ChannelRestRequest, self).__init__()
        self.session = message.channel_session
        if 'channels_rest' not in self.session:
            self.session['channels_rest'] = {}

        self.user = message.user
        self._user = message.user
        self.method = method

    def is_ajax(self):
        return True

    def get_host(self):
        if 'host' in self.session['channels_rest']:
            return self.session['channels_rest']['host']

    def fix_meta(self):
        if 'host' in self.session['channels_rest']:
            self.META['HTTP_HOST'] = self.session['channels_rest']['host']
        if 'user-agent' in self.session['channels_rest']:
            self.META['HTTP_USER_AGENT'] = self.session['channels_rest']['user-agent']


def process_rest_request(message, urls=settings.ROOT_URLCONF):
    try:
        data = json.loads(message.content['text'])
    except:
        logger.debug("Error parsing JSON")
        return False

    if 'datatype' not in data or data['datatype'] != 'request':
        return False

    for i in ['url', 'method']:
        if i not in data:
            return False

    def return_403(reason='Access denied'):
        message.reply_channel.send({
            "text": json.dumps({
                'status_code': 403,
                'reason': reason
            })
        })
        return False

    def return_404(reason='Not found'):
        message.reply_channel.send({
            "text": json.dumps({
                'status_code': 404,
                'reason': reason
            })
        })
        return False

    def return_500(reason='Internal server error'):
        message.reply_channel.send({
            "text": json.dumps({
                'status_code': 500,
                'reason': reason
            })
        })
        return False

    try:
        resolver = RegexURLResolver(r'^/', urls)
    except:
        logger.exception("Something went wrong when constructing the urlresolver")
        return return_500()

    try:
        callback, callback_args, callback_kwargs = resolver.resolve(data['url'])
    except:
        logger.exception("No matches found for url %s", data['url'])
        return return_404()

    request = ChannelRestRequest(message, method=data['method'].upper())
    request.path = data['url']

    if 'body' in data:
        request._body = data['body']
        request._read_started = True

    if 'meta' in data:
        request.META = data['meta']

    request.fix_meta()

    response = None

    request_middleware = []
    for middleware_path in settings.MIDDLEWARE_CLASSES:
        if not middleware_path.startswith('django'):
            mw_class = import_string(middleware_path)
            try:
                mw_instance = mw_class()
                if hasattr(mw_instance, 'process_request'):
                    request_middleware.append(mw_instance.process_request)
            except MiddlewareNotUsed as exc:
                if settings.DEBUG:
                    if six.text_type(exc):
                        logger.debug('MiddlewareNotUsed(%r): %s', middleware_path, exc)
                    else:
                        logger.debug('MiddlewareNotUsed: %r', middleware_path)
                continue

    try:
        for middleware_method in request_middleware:
            response = middleware_method(request)
            if response:
                break

        response = callback(request, *callback_args, **callback_kwargs)
    except:
        logger.exception("Something went wrong procesing the view.")
        return return_500()

    response.render()
    response_packet = {
        'datatype': data['datatype'],
        'meta': dict(response.items()),
        'status_code': response.status_code,
    }
    if response.content:
        response_packet['body'] = response.content.decode('utf-8')

    if hasattr(response, 'status_text'):
        response_packet['reason'] = response.status_text

    if 'message_id' in data:
        response_packet['message_id'] = data['message_id']

    message.reply_channel.send({"text": json.dumps(response_packet)})
    return True


def enable_rest_request_session(message):
    message.channel_session['channels_rest'] = {}
    for i in ['host', 'origin', 'user-agent']:
        for k, v in message.content['headers']:
            k = force_text(k)
            v = force_text(v)
            if k == i:
                message.channel_session['channels_rest'][i] = v
