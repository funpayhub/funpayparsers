__all__ = ('UpdatesParser', 'UpdatesParserOptions')

from funpayparsers.parsers.base import FunPayJSONObjectParser, FunPayObjectParserOptions
from funpayparsers.types.updates import (OrdersCounters,
                                         ChatBookmarks,
                                         ChatCounter,
                                         NodeInfo,
                                         CurrentlyViewingOfferInfo,
                                         ChatNode,
                                         ActionResponse,
                                         UpdateObject,
                                         Updates)
from funpayparsers.parsers.messages_parser import MessagesParser, MessagesParserOptions
from funpayparsers.parsers.chat_preview_parser import PrivateChatPreviewParser, PrivateChatPreviewParserOptions
from funpayparsers.parsers.cpu_parser import CurrentlyViewingOfferInfoParser, CurrentlyViewingOfferInfoParserOptions
from funpayparsers.types.enums import UpdateType
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdatesParserOptions(FunPayObjectParserOptions):
    ...



class UpdatesParser(FunPayJSONObjectParser[Updates, UpdatesParserOptions]):
    """
    Class for parsing updates.
    Possible locations:
        - In runners response.
    """
    def _parse(self):
        updates_obj = Updates(
            raw_source=str(self.raw_source),
            orders_counters=None,
            chat_counter=None,
            chat_bookmarks=None,
            cpu=None,
            nodes=[],
            unknown_objects=[],
            response=None
        )

        action_response = self.data.get('response')
        if action_response:
            updates_obj.response = self._parse_action_response(action_response)

        objects = self.data.get('objects')
        if not objects:
            return updates_obj

        unknown_objects = []
        nodes = {}
        for obj in objects:
            result = self._parse_update(obj)
            if result is None:
                unknown_objects.append(obj)
            elif result.type is UpdateType.CHAT_NODE:
                updates_obj.nodes.append(result)
            else:
                setattr(updates_obj, self.__update_fields__[result.type], result)

        updates_obj.unknown_objects = unknown_objects or updates_obj.unknown_objects
        updates_obj.nodes = nodes or updates_obj.nodes
        return updates_obj

    def _parse_orders_counters(self, obj: dict) -> OrdersCounters:
        return OrdersCounters(
            raw_source=str(obj),
            purchases=int(obj.get('buyer')) if obj.get('seller') else 0,
            sales=int(obj.get('seller')) if obj.get('seller') else 0
        )

    def _parse_chat_counter(self, obj: dict) -> ChatCounter:
        return ChatCounter(
            raw_source=str(obj),
            counter=int(obj['counter']),
            message=int(obj['message'])
        )

    def _parse_chat_bookmarks(self, obj: dict) -> ChatBookmarks:
        previews = PrivateChatPreviewParser(obj['html'], options=PrivateChatPreviewParserOptions() & self.options).parse()
        return ChatBookmarks(
            raw_source=str(obj),
            counter=int(obj['counter']),
            message=int(obj['message']),
            order=obj['order'],
            chat_previews=previews
        )

    def _parse_cpu(self, obj: dict) -> CurrentlyViewingOfferInfo:
        html_ = obj['html']['desktop']
        return CurrentlyViewingOfferInfoParser(
            html_,
            options=CurrentlyViewingOfferInfoParserOptions() & self.options
        ).parse()

    def _parse_node(self, obj: dict) -> ChatNode:
        node_obj = obj['node']
        node_info = NodeInfo(
            raw_source=str(node_obj),
            id=int(node_obj['id']),
            name=node_obj['name'],
            silent=node_obj['silent'],
        )

        messages = MessagesParser(
            '\n'.join(i['html'] for i in node_obj['messages']),
            options=MessagesParserOptions() & self.options,
        ).parse()

        return ChatNode(
            raw_source=str(obj),
            node=node_info,
            messages=messages,
            has_history=obj['has_history'],
        )

    def _parse_action_response(self, obj: dict) -> ActionResponse:
        return ActionResponse(
            raw_source=str(obj),
            error=obj.get('error')
        )

    def _parse_update(self, update_dict: dict) -> UpdateObject | None:
        update_type = UpdateType.get_by_type_str(update_dict.get('type'))
        if update_type not in self.__parsing_methods__:
            return None

        method = self.__parsing_methods__[update_type]
        obj = method(self, update_dict['data'])

        return UpdateObject(
            raw_source=str(update_dict),
            type=update_type,
            id=update_dict['id'],
            tag=update_dict['tag'],
            data=obj
        )

    __parsing_methods__ = {
        UpdateType.ORDERS_COUNTERS: _parse_orders_counters,
        UpdateType.CHAT_COUNTER: _parse_chat_counter,
        UpdateType.CHAT_BOOKMARKS: _parse_chat_bookmarks,
        UpdateType.CHAT_NODE: _parse_node,
        UpdateType.CPU: _parse_cpu,
    }

    __update_fields__ = {
        UpdateType.ORDERS_COUNTERS: 'orders_counters',
        UpdateType.CHAT_COUNTER: 'chat_counter',
        UpdateType.CHAT_BOOKMARKS: 'chat_bookmarks',
        UpdateType.CPU: 'cpu',
    }
