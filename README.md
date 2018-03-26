# django-comm

Краткое описание:

Фронт - nginx, который перенаправляет http на django, а socket на django-websocket-redis.

Пользователь устанавливает соединение по сокету и подписывается на уведомления. Потом обычным образом через api запрашивает выгрузку файла, на сервере создается внутренняя задача и помещается в очередь, по завершению пользователю приходит ссылка на файл через оповещение по сокету. Выгрузка сделана в двух форматах: XML и CSV.

В качестве обработчика очереди используется Celery, в которой сами очереди находятся в RabbitMQ, а ответы сохраняются в Redis.

В качестве реляционной базы используется Postgresql.

Для работы с иерархическими данными используется django-mptt, которая реализует алгоритм modified pre-order traversal tree.
