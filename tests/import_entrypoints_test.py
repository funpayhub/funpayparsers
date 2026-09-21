from __future__ import annotations

import sys
import subprocess

import pytest


ENTRYPOINTS = [
    'import funpayparsers',
    'from funpayparsers.parsers import ProfilePageParser',
    'from funpayparsers.parsers.page_parsers import MainPageParser',
    'from funpayparsers.types import UserRating',
    'from funpayparsers.types.pages import ProfilePage',
    'from funpayparsers.types.pages.profile_page import ProfilePage',
    'from funpayparsers.types.pages.order_page import OrderPage',
    'import funpayparsers.types.pages',
]


@pytest.mark.parametrize('statement', ENTRYPOINTS)
def test_entrypoint_imports_in_a_fresh_interpreter(statement: str):
    # Each statement runs in its own process on purpose: a circular import only
    # shows up when the module in question is imported FIRST. Once any other
    # entrypoint has populated sys.modules, the cycle is already resolved and
    # the same statement succeeds — which is why importing via
    # `funpayparsers.parsers` (the README example) hides the problem.
    result = subprocess.run(
        [sys.executable, '-c', statement],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f'`{statement}` failed:\n{result.stderr}'
