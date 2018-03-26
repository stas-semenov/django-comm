import os
import gevent.socket
import redis.connection

redis.connection.socket = gevent.socket

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comm_django.settings")

from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
application = uWSGIWebsocketServer()
