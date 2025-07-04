__all__ = ('chat_data_factory',
           'public_chat_html',
           'public_chat_obj',
           'private_blocked_chat_html',
           'private_blocked_chat_obj',
           'private_chat_with_notifications_html',
           'private_chat_with_notifications_obj',
           'private_chat_without_notifications_html',
           'private_chat_without_notifications_obj',
           'chat_data')

from funpayparsers.types import Chat
import pytest


@pytest.fixture
def chat_data_factory(messages_data, user_preview_data):
    def factory(id: int,
                name: str,
                with_user: bool = True,
                notifications: bool = True,
                banned: bool = False) -> tuple[str, Chat]:
        messages_html, messages = messages_data
        user_preview_html, user_preview = user_preview_data if with_user else ('', None)

        html = f"""<div class="chat chat-float" data-id="{id}" data-name="{name}" data-user="12345" data-history="1" data-tag="abcdefgh" data-bookmarks-tag="abcdefgh">
    {{header}}

    <div class="chat-panel-mobile hidden"></div>

    <div class="chat-message-container">
        <div class="chat-message-list scrollbar-invisible">
        {messages_html}
        </div>
    </div>

    <div class="chat-form">
        <form action="https://funpay.com/chat/message" method="post">
            <div class="chat-form-input">
                <div class="form-group" id="comments">
                    <textarea class="form-control" name="content" cols="30" rows="1" placeholder="Написать..." autofocus=""></textarea>
                    <div class="hiddendiv"></div>
                </div>
            </div>
            <div class="chat-form-attach">
                <button type="button" class="btn btn-default chat-btn-image" data-size-max="7340032" data-size-max-str="7 МБ">
                    <i class="fa fa-paperclip"></i></button>
            </div>
            <div class="chat-form-btn">
                <button type="submit" class="btn btn-gray btn-round"><i class="fa fa-arrow-right"></i></button>
            </div>
        </form>
    </div>
</div>"""

        if not with_user:
            header = f"""
<div class="chat-header bg-light-color bg-light-style">
                    <div class="media-user-name h2">
                <a href="https://funpay.com/chat/?node={name}">ChatName</a>            </div>
                <div class="chat-header-controls">
                            <a class="btn btn-info-icon btn-info-sm btn-default chat-control" href="https://funpay.com/chat/?node={name}"><i class="far fa-clone icon"></i></a>
                                                    <a class="btn btn-info-icon btn-info-sm btn-default chat-control" href="https://support.funpay.com/tickets/new" target="_blank" title="Пожаловаться">
                    <i class="fa fa-exclamation-triangle icon"></i>
                </a>
                                </div>
            </div>"""
        else:
            header = f"""
<div class="chat-header">
                                {user_preview_html}
                <div class="chat-header-controls">
                                        <span class="notice-button-container chat-control" data-color="gray">
        <button type="button" class="btn btn-info-icon btn-info-sm {'btn-danger' if banned else 'btn-success' if notifications else 'btn-gray'}">
            <i class="fa fa-check icon"></i>
            <span class="inside hidden-md hidden-xs">Включены<br>оповещения</span>
        </button>
    </span>                                        <div class="dropdown inline-block">
                    <button class="btn btn-info-icon btn-info-sm btn-gray" type="button" data-toggle="dropdown">
                        <i class="fa fa-ellipsis-h icon"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-right">
                        <li>
                            <a href="https://support.funpay.com/tickets/new" target="_blank">Пожаловаться</a>
                        </li>
                        <li>
                            <a href="javascript:void(0)" class="form-ajax-simple" data-action="https://funpay.com/chat/mute" data-fields="{{&quot;node_id&quot;:142907396,&quot;mute&quot;:1}}">Заблокировать</a>
                        </li>
                    </ul>
                </div>
                                </div>
                    <a class="chat-back"><i class="fa fa-chevron-left"></i></a>
            </div>"""

        html = html.format(header=header)

        obj = Chat(
            raw_source='',
            id=id,
            name=name,
            interlocutor=user_preview if with_user else None,
            is_notifications_enabled=notifications if with_user else None,
            is_blocked=banned if with_user else None,
            history=messages
        )

        return html, obj
    return factory


@pytest.fixture
def public_chat_html(chat_data_factory) -> str:
    html, _ = chat_data_factory(id=2, name='flood', with_user=False)
    return html


@pytest.fixture
def public_chat_obj(chat_data_factory) -> Chat:
    _, obj = chat_data_factory(id=2, name='flood', with_user=False)
    return obj


@pytest.fixture
def private_blocked_chat_html(chat_data_factory) -> str:
    html, _ = chat_data_factory(id=1, name='users-1-2', banned=True)
    return html


@pytest.fixture
def private_blocked_chat_obj(chat_data_factory) -> Chat:
    _, obj = chat_data_factory(id=1, name='users-1-2', banned=True)
    return obj


@pytest.fixture
def private_chat_with_notifications_html(chat_data_factory) -> str:
    html, _ = chat_data_factory(id=2, name='users-1-2', notifications=True)
    return html


@pytest.fixture
def private_chat_with_notifications_obj(chat_data_factory) -> Chat:
    _, obj = chat_data_factory(id=2, name='users-1-2', notifications=True)
    return obj


@pytest.fixture
def private_chat_without_notifications_html(chat_data_factory) -> str:
    html, _ = chat_data_factory(id=2, name='users-1-2', notifications=False)
    return html


@pytest.fixture
def private_chat_without_notifications_obj(chat_data_factory) -> Chat:
    _, obj = chat_data_factory(id=2, name='users-1-2', notifications=False)
    return obj


@pytest.fixture(params=[
    ('public_chat_html', 'public_chat_obj'),
    ('private_blocked_chat_html', 'private_blocked_chat_obj'),
    ('private_chat_with_notifications_html', 'private_chat_with_notifications_obj'),
    ('private_chat_without_notifications_html', 'private_chat_without_notifications_obj')
],
    ids=['public_chat', 'private_blocked_chat', 'private_chat_with_notifications',
         'private_chat_without_notifications']
    )
def chat_data(request):
    html, obj = request.param
    html = request.getfixturevalue(html)
    obj = request.getfixturevalue(obj)
    return html, obj
