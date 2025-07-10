from __future__ import annotations


__all__ = ('FunPayPage',)


from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common_page_elements import AppData, PageHeader


@dataclass
class FunPayPage(FunPayObject):
    """Base class for FunPay pages."""

    header: PageHeader
    """Page header."""

    app_data: AppData
    """App data."""
