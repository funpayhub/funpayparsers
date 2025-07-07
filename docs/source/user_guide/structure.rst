************************
Структура FunPay Parsers
************************

Структура FunPay Parsers проста и прозрачна, однако для эффективного использования библиотеки важно понимать базовые принципы её структуры.

====
Типы
====

Все дата-классы, представляющие объекты FunPay (например: сообщения, чаты, транзакции, главная страница),
наследуются от базового класса ``FunPayObject``, содержащего всего одно поле: ``raw_source`` — строку HTML или JSON, из которой был создан объект.

Любой тип (кроме типов, представляющих целые страницы) нужно импортировать из ``funpayparsers.types``:

.. code:: python

    from funpayparsers.types import Chat, Message


Типы полных страниц нужно импортировать из ``funpayparsers.types.pages``:

.. code:: python

    from funpayparsers.types.pages import MainPage, ProfilePage


=======
Парсеры
=======

Все парсеры наследуются от абстрактных классов ``FunPayHTMLObjectParser`` и ``FunPayJSONObjectParser`` (в зависимости от формата строки для парсинга),
которые в свою очередь наследуются от ``FunPayObjectParser``.

Любой парсер (кроме тех, что парсят целые страницы) нужно импортировать из ``funpayparsers.parsers``:

.. code:: python

    from funpayparsers.parsers import MessagesParser

Парсеры для полных страниц нужно импортировать из ``funpayparsers.parsers.page_parsers``:

.. code:: python

    from funpayparsers.parsers.page_parsers import MainPageParser

При создании экземпляра любого парсера необходимо передать обязательный аргумент ``raw_source`` - строку,
содержащую HTML или JSON, подлежащую парсингу.
Так же можно передать необязательный аргумент ``options`` - дата-класс с опциями парсера.

.. code:: python

    from funpayparsers.parsers import MessagesParser, MessagesParsingOptions


    messages_parsing_options = MessagesParsingOptions(empty_raw_source=True)
    parser = MessagesParser('HTML строка', options=messages_parsing_options)

Есть возможность изменить значения отдельных полей объекта, передав их в `**overloads`.
Эти поля перекрывают соответствующие значения, заданные через `options`.

.. code:: python

    from funpayparsers.parsers import MessagesParser, MessagesParsingOptions


    GLOBAL_OPTS = MessagesParsingOptions(empty_raw_source=True)
    parser = MessagesParser('HTML строка', options=GLOBAL_OPTS, empty_raw_source=False)


Для того, чтобы непосредственно спарсить переданную строку в дата-класс, необходимо вызвать метод ``.parse()``.


.. code:: python

    from funpayparsers.parsers import MessagesParser, MessagesParsingOptions


    messages_parsing_options = MessagesParsingOptions(empty_raw_source=True)
    messages = MessagesParser('HTML строка', options=messages_parsing_options).parse()


==================
Настройки парсеров
==================

Для настройки парсеров используются дата-классы, каждый из которых наследован от базового класса ``ParsingOptions``.
Каждому конкретному парсеру соответствует свой собственный класс настроек, содержащий параметры, специфичные для данного парсера.

Один из таких параметров — ``empty_raw_source`` — определяет, будет ли в итоговом объекте поле ``raw_source``
содержать исходную строку (HTML или JSON), переданную в парсер.

Этот параметр определён в базовом классе ``ParsingOptions`` и унаследован всеми дочерними классами.
По умолчанию ``empty_raw_source = False``, то есть оригинальная строка сохраняется в ``raw_source``.

Если же вы установите ``empty_raw_source = True``, поле ``raw_source`` будет принудительно очищено
(будет содержать пустую строку ``''``).
Это может быть полезно, если вам не требуется хранить исходный HTML/JSON — например, для экономии памяти.


.. code:: python

    from funpayparsers.parsers import UserBadgeParser, UserBadgeParsingOptions

    badge = UserBadgeParser('HTML строка').parse()
    print(badge.raw_source)

    # Вывод
    'HTML строка'


.. code:: python

    from funpayparsers.parsers. import UserBadgeParser, UserBadgeParsingOptions

    badge = UserBadgeParser('HTML строка', options=UserBadgeParsingOptions(empty_raw_source=True)).parse()
    print(badge.raw_source)

    # Вывод
    ''

--------------------
Объединение настроек
--------------------

Дата-классы с настройками парсеров можно объединять, используя операторы ``&`` и ``|``.

.. important::

    При использовании операторов ``&`` и ``|`` **создается новый экземпляр** класса настроек с тем же типом, что и у первого операнда.


.. attention::

    Вы можете комбинировать настройки разных типов, однако результатом всегда будет экземпляр того же класса, что и первый операнд.
    Это означает, что в итоговом объекте будут только те поля, которые определены в классе первого операнда,
    даже если второй операнд содержит другие поля.


Оператор ``&`` создает копию ``options1``, в которой все значения заменены значениями из ``options2``, но только теми,
что были явно указаны при создании ``options2``.

.. code:: python

    from funpayparsers.parsers import ParsingOptions


    options1 = ParsingOptions(empty_raw_source=True)
    options2 = ParsingOptions()  # по умолчанию empty_raw_source=False

    # options3.empty_raw_source=True, т.к. в options2 это поле не было явно указано.
    options3 = options1 & options2


    options1 = ParsingOptions()  # по умолчанию empty_raw_source=False
    options2 = ParsingOptions(empty_raw_source=True)

    # options3.empty_raw_source=True, т.к. в options2 это поле было явно указано.
    options3 = options1 & options2

Оператор ``|`` создает копию ``options1``, в которой все значения заменены значениями из ``options2``, вне зависимости от того, были ли они явно заданы.

.. danger::

    Оператор ``|`` не рекомендуется использовать, т.к. такой код сложнее понимать, что может привести к неожиданному поведению парсеров.


.. code:: python

    from funpayparsers.parsers import ParsingOptions

    options1 = ParsingOptions(empty_raw_source=True)
    options2 = ParsingOptions()  # по умолчанию empty_raw_source=False

    # options3.empty_raw_source=False, т.к. "|" перезаписывает все поля из options2 в options1,
    # но явно это нигде не указано.
    options3 = options1 | options2


.. tip::

    Данный способ объединения можно применять, когда у вас есть какие-то глобальные параметры. Например, вы хотите, чтобы все парсеры
    оставляли поле ``raw_source`` пустым.
    Это позволяет переиспользовать одни и те же базовые настройки в разных парсерах, изменяя только необходимые поля.


    .. code:: python

        from funpayparsers.parsers import ParsingOptions
        from funpayparsers.parsers import MessagesParser, MessagesParsingOptions
        from funpayparsers.parsers import MoneyValueParser, MoneyValueParsingOptions, MoneyValueParsingMode


        OPTIONS = ParsingOptions(empty_raw_source=True)

        messages = MessagesParser('HTML строка', options=MessagesParsingOptions(sort_by_id=True) & OPTIONS).parse()

        parsing_opts = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_TRANSACTION)
        money_value = MoneyValueParser('HTML строка', options=parsing_opts & OPTIONS)