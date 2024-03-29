"""Test the module `deepupdate`."""
# pylint:disable=redefined-outer-name
from typing import Any

import pytest

from .deepupdate import deepupdate


@pytest.fixture
def d() -> dict[str, Any]:
    """A fitting argument for parameter `d` in `deepupdate(d,u)`."""
    return {"a": 42, "b": {"c": {"d": 23}, "e": "foo"}}


def test_deepupdate_with_empty_u(d) -> None:
    """Test that `deepupdate()` on a dict with an empty dict for `u` leaves the
    original dict intact."""
    assert d == deepupdate(d, {})


def test_deepupdate_with_simple_change(d) -> None:
    """Test that `deepupdate()` on a dict with simple valued dict works."""
    result = deepupdate(d, {"a": 420})
    assert result == {"a": 420, "b": {"c": {"d": 23}, "e": "foo"}}


def test_deepupdate_with_nested_empty_dict(d) -> None:
    """Test that `deepupdate()` on a dict with a nested empty dict
    works."""
    result = deepupdate(d, {"b": {}})
    assert d == result


def test_deepupdate_with_nested_dict_as_simple_value(d) -> None:
    """Test that `deepupdate()` on a dict with with a nested dict
    works."""
    result = deepupdate(d, {"a": 420, "b": None})
    assert result == {"a": 420, "b": {"c": {"d": 23}, "e": "foo"}}


def test_deepupdate_with_nested_dict(d) -> None:
    """Test that `deepupdate()` on a dict with an dict with a nested dict
    works."""
    result = deepupdate(d, {"b": {"e": "bar"}})
    assert result == {"a": 42, "b": {"c": {"d": 23}, "e": "bar"}}
