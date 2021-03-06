# Бэкенд для сервиса комментариев

- Каждый комментарий имеет привязку к определенному пользователю.
- У каждого комментария есть дата создания.
- Коментарии имеют древовидную структуру - есть возможность оставлять комментарии на комментарии с неограниченной степенью вложенности.
- Каждый комментарий имеет привязку к определенной сущности (пост в блоге, страница пользователя, другой комментарий и т.п.), которая однозначно идентифицируется парой значений (идентификатор типа сущности, идентификатор сущности).
- Бэкенд предоставляет следующие интерфейсы (REST API with JSON):
  - Создание комментария к определенной сущности с указанием сущности, к которой он относится.
  - Получение комментариев первого уровня для определенной сущности с пагинацией.
  - Получение всех дочерних комментариев для заданного комментария или сущности без ограничения по уровню вложенности. Корнем может являться пара идентифицирующая сущность или id комментария, являющегося корневым для данной ветки. Ответ приходит таким, что на клиенте можно воссоздать иерархию комментариев.
  - Получение истории комментариев определенного пользователя.
  - Выгрузка в файл (xml и csv формат) всей истории комментариев по пользователю или сущности с возможностью указания интервала времени, в котором был создан комментарий пользователя (если не задан - выводить всё). Время ответа на первичный запрос не зависит от объема данных в итоговой выгрузке. Нотификация пользователся о готовности файла для скачивания приходит по websocket.
- Время ответа на все запросы ограничено 1 секундной. С условием:
  - глубина дерева не менее 100,
  - количество узлов (элементов, имеющих дочерние элементы) в дереве не менее 10000.
