import pytest

from app.utils.code_parser import parse_rally


def test_simple_serve_terminal_plus():
    p = parse_rally("H6S+8C H5R+6B A#6C")
    assert p.terminal_eval == "#"
    assert p.terminal_index == 2
    assert len(p.actions) == 3


def test_serve_cannot_have_start():
    with pytest.raises(Exception):
        parse_rally("H6S+1A8C")


def test_negative_then_post_block():
    p = parse_rally("G7A#6C B-6C")
    assert p.terminal_eval == "#"
    assert p.post_annotations and p.post_annotations[0].raw.startswith("B-")


def test_must_have_terminal():
    with pytest.raises(Exception):
        parse_rally("H6S+8C H5R+6B A+6C")
