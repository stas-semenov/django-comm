# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher

from comm_app.models import Comment

import io
import os
import time
import uuid

import json
import unicodecsv as csv
from dicttoxml import dicttoxml
from datetime import datetime
from dateutil.parser import parse

from comm_app.utils import check_int_positive


def export_file_proc(user_id, entity_id, date_from, date_to, export_type):
    if not (export_type == 'XML' or export_type == 'CSV'):
        raise ValueError('Export type is undefined')

    user_id = check_int_positive(user_id)
    entity_id = check_int_positive(entity_id)

    comments = []
    if user_id > 0:
        try:
            # comments = [{"user_id": user_id, "date_from": date_from, "date_to": date_to}]
            if date_from is not None and date_to is not None:
                comms = Comment.objects.filter(user_id=user_id, date__range=(date_from, date_to))
            elif date_from is not None:
                comms = Comment.objects.filter(user_id=user_id, date__gte=date_from)
            elif date_to is not None:
                comms = Comment.objects.filter(user_id=user_id, date__lte=date_to)
            else:
                comms = Comment.objects.filter(user_id=user_id)
            if comms is not None:
                for c in comms:
                    comments.append({"text":c.text, "id":c.id, "date":c.date})
        except:
            pass
    elif entity_id > 0:
        try:
            # comments = [{"entity_id": entity_id, "date_from": date_from, "date_to": date_to}]
            if date_from is not None and date_to is not None:
                comms = Comment.objects.filter(entity_id=entity_id, date__range=(date_from, date_to))
            elif date_from is not None:
                comms = Comment.objects.filter(entity_id=entity_id, date__gte=date_from)
            elif date_to is not None:
                comms = Comment.objects.filter(entity_id=entity_id, date__lte=date_to)
            else:
                comms = Comment.objects.filter(entity_id=entity_id)
            if comms is not None:
                for c in comms:
                    comments.append({"text":c.text, "id":c.id, "date":c.date})
        except:
            pass
    else:
        raise ValueError('Neither User nor Entity is defined')


    if len(comments) > 0:
        filename = str(uuid.uuid4())
        if export_type == 'XML':
            filepath = os.path.join('/tmp', filename + '.xml')
            data_xml = dicttoxml(comments, custom_root='comments', attr_type=False)
            with io.open(filepath, 'w', encoding='utf-8') as f:
                f.write(u'{}'.format(data_xml))
            filename = '/xml/' + filename
        elif export_type == 'CSV':
            filepath = os.path.join('/tmp', filename + '.csv')
            filename = '/csv/' + filename
            keys = map(unicode,comments[0].keys())
            with io.open(filepath, 'wb') as f:
                w = csv.DictWriter(f, keys)
                w.writeheader()
                w.writerows(comments)
        return filename
    else:
        return 'No data'

@shared_task
def export_file(args):
    sess, msg = args

    try:
        json_data = json.loads(msg)

        try:
            date_from = None
            if 'date_from' in json_data and json_data['date_from']:
                date_from = str(json_data['date_from'])
                date_from = parse(date_from)
        except:
            date_from = None

        try:
            date_to = None
            if 'date_to' in json_data and json_data['date_to']:
                date_to = str(json_data['date_to'])
                date_to = parse(date_to)
        except:
            date_to = None

        export_type = None
        if 'export_type' in json_data and json_data['export_type']:
            export_type = str(json_data['export_type']).upper()

        user_id = None
        if 'user_id' in json_data and json_data['user_id']:
            user_id = str(json_data['user_id'])
        
        entity_id = None
        if 'entity_id' in json_data and json_data['entity_id']:
            entity_id = str(json_data['entity_id'])


    except (ValueError, Exception) as e:
        if type(e).__name__ == 'ValueError':
            msg = str(e)
        else:
            msg = 'Error'
    msg = export_file_proc(user_id, entity_id, date_from, date_to, export_type)

    return (sess, msg)


@shared_task
def notify_file_ready(args):
    sess, msg = args
    # simulate hard work
    time.sleep(1)
    redis_publisher = RedisPublisher(facility='comm', sessions=[sess])
    message = RedisMessage(msg)
    redis_publisher.publish_message(message)
    return msg
