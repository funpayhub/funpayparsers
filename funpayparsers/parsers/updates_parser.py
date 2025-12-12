from __future__ import annotations


__all__ = ('UpdatesParser', 'UpdatesParsingOptions')

import json
from typing import Any, cast
from dataclasses import dataclass

from funpayparsers.types.enums import RunnerDataType
from funpayparsers.parsers.base import ParsingOptions, FunPayJSONObjectParser
from funpayparsers.types.common import CurrentlyViewingOfferInfo
from funpayparsers.types.updates import (
    ChatNode,
    NodeInfo,
    ChatCounter,
    ChatBookmarks,
    ActionResponse,
    OrdersCounters,
    RunnerResponse,
    RunnerResponseObject,
)
from funpayparsers.parsers.cpu_parser import (
    CurrentlyViewingOfferInfoParser,
    CurrentlyViewingOfferInfoParsingOptions,
)
from funpayparsers.parsers.messages_parser import MessagesParser, MessagesParsingOptions
from funpayparsers.parsers.chat_previews_parser import (
    PrivateChatPreviewsParser,
    PrivateChatPreviewParsingOptions,
)


@dataclass(frozen=True)
class UpdatesParsingOptions(ParsingOptions):
    """Options class for ``UpdatesParser``."""

    private_chat_previews_parsing_options: PrivateChatPreviewParsingOptions = (
        PrivateChatPreviewParsingOptions()
    )
    """
    Options instance for ``CurrentlyViewingOfferInfoParser``, 
    which is used by ``UpdatesParser``.

    Defaults to ``PrivateChatPreviewParsingOptions()``.
    """

    messages_parsing_options: MessagesParsingOptions = MessagesParsingOptions()
    """
    Options instance for ``MessagesParser``, 
    which is used by ``UpdatesParser``.

    Defaults to ``MessagesParsingOptions()``.
    """

    cpu_parsing_options: CurrentlyViewingOfferInfoParsingOptions = (
        CurrentlyViewingOfferInfoParsingOptions()
    )
    """
    Options instance for ``PrivateChatPreviewsParser``, 
    which is used by ``UpdatesParser``.

    Defaults to ``CurrentlyViewingOfferInfoParsingOptions()``.
    """


class UpdatesParser(FunPayJSONObjectParser[RunnerResponse, UpdatesParsingOptions]):
    """
    Class for parsing updates.

    Possible locations:
        - Runner response.
    """

    def _parse(self) -> RunnerResponse:
        updates_obj = RunnerResponse(
            raw_source=str(self.raw_source),
            orders_counters=None,
            chat_counter=None,
            chat_bookmarks=None,
            cpu=[],
            nodes=[],
            unknown_objects=[],
            response=None,
        )

        action_response = self.data.get('response')  # type: ignore[union-attr]  # raise if not dict
        if action_response:
            updates_obj.response = self._parse_action_response(action_response)
            if updates_obj.response.error:
                return updates_obj

        objects = self.data.get('objects')  # type: ignore[union-attr]  # raise if not dict
        if not objects:
            return updates_obj

        for obj in objects:
            result = self._parse_update(obj)
            if result is None:
                updates_obj.unknown_objects.append(obj)  # type: ignore[union-attr]
            elif result.type is RunnerDataType.CHAT_NODE:
                updates_obj.nodes.append(result)  # type: ignore[union-attr]
            elif result.type is RunnerDataType.CPU:
                updates_obj.cpu.append(result)
            else:
                setattr(updates_obj, self.__update_fields__[result.type], result)

        updates_obj.nodes = updates_obj.nodes or None
        updates_obj.unknown_objects = updates_obj.unknown_objects or None
        updates_obj.cpu = updates_obj.cpu or None

        return updates_obj

    def _parse_orders_counters(self, obj: dict[str, Any]) -> OrdersCounters:
        return OrdersCounters(
            raw_source=json.dumps(obj, ensure_ascii=False),
            purchases=int(cast(str, obj.get('buyer'))) if obj.get('buyer') else 0,
            sales=int(cast(str, obj.get('seller'))) if obj.get('seller') else 0,
        )

    def _parse_chat_counter(self, obj: dict[str, Any]) -> ChatCounter:
        return ChatCounter(
            raw_source=str(obj),
            counter=int(obj['counter']),
            latest_message_id=int(obj['message']),
        )

    def _parse_chat_bookmarks(self, obj: dict[str, Any]) -> ChatBookmarks:
        return ChatBookmarks(
            raw_source=str(obj),
            counter=int(obj['counter']),
            latest_message_id=int(obj['message']),
            order=obj['order'],
            chat_previews=PrivateChatPreviewsParser(
                obj['html'],
                options=self.options.private_chat_previews_parsing_options,
            ).parse(),
        )

    def _parse_cpu(self, obj: dict[str, Any]) -> CurrentlyViewingOfferInfo:
        html_ = obj.get('html')
        if not html_:
            return CurrentlyViewingOfferInfo(
                raw_source=json.dumps(obj, ensure_ascii=False), id=None, title=None
            )

        html_ = obj['html']['desktop']
        return CurrentlyViewingOfferInfoParser(
            html_,
            options=self.options.cpu_parsing_options,
        ).parse()

    def _parse_node(self, obj: dict[str, Any]) -> ChatNode:
        node_obj = obj['node']
        node_info = NodeInfo(
            raw_source=str(node_obj),
            id=int(node_obj['id']),
            name=node_obj['name'],
            silent=node_obj['silent'],
        )

        messages = MessagesParser(
            '\n'.join(i['html'] for i in obj['messages']),
            options=self.options.messages_parsing_options,
            context={'chat_id': node_info.id, 'chat_name': node_info.name},
        ).parse()

        return ChatNode(
            raw_source=str(obj),
            node=node_info,
            messages=messages,
            has_history=obj['hasHistory'],
        )

    def _parse_action_response(self, obj: dict[str, Any]) -> ActionResponse:
        return ActionResponse(
            raw_source=str(obj),
            error=obj.get('error'),
        )

    def _parse_update(self, update_dict: dict[str, Any]) -> RunnerResponseObject[Any] | None:
        update_type = RunnerDataType.get_by_type_str(cast(str, update_dict.get('type')))
        if update_type not in self.__parsing_methods__:
            return None

        method = self.__parsing_methods__[update_type]
        data = update_dict.get('data')
        obj = method(self, update_dict['data']) if data else False

        return RunnerResponseObject(
            raw_source=str(update_dict),
            type=update_type,
            id=update_dict['id'],
            tag=update_dict['tag'],
            data=obj,
        )

    __parsing_methods__ = {
        RunnerDataType.ORDERS_COUNTERS: _parse_orders_counters,
        RunnerDataType.CHAT_COUNTER: _parse_chat_counter,
        RunnerDataType.CHAT_BOOKMARKS: _parse_chat_bookmarks,
        RunnerDataType.CHAT_NODE: _parse_node,
        RunnerDataType.CPU: _parse_cpu,
    }

    __update_fields__ = {
        RunnerDataType.ORDERS_COUNTERS: 'orders_counters',
        RunnerDataType.CHAT_COUNTER: 'chat_counter',
        RunnerDataType.CHAT_BOOKMARKS: 'chat_bookmarks',
        RunnerDataType.CPU: 'cpu',
    }
