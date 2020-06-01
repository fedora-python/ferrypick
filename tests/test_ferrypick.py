import pytest
from pathlib import Path

import ferrypick


U = "https://src.fedoraproject.org"


def test_parse_link_pr():
    n, p = ferrypick.parse_link(f"{U}/rpms/python-rpm-macros/pull-request/62")
    assert p == f"{U}/rpms/python-rpm-macros/pull-request/62.patch"
    assert n == "python-rpm-macros"


def test_parse_link_commit():
    hash = "f54cef86717adf4f5374820c3d5314f75b340b8b"
    n, p = ferrypick.parse_link(f"{U}/rpms/python3.7/c/{hash}?branch=master")
    assert p == f"{U}/rpms/python3.7/c/{hash}.patch"
    assert n == "python3.7"


def test_parse_link_commit_from_pr():
    hash = "6697c4ae608728bce1025ef45af"
    n, p = ferrypick.parse_link(f"{U}/fork/ca/rpms/python3.7/c/{hash}?branch=rename")
    assert p == f"{U}/fork/ca/rpms/python3.7/c/{hash}.patch"
    assert n == "python3.7"


def test_parse_link_bad():
    with pytest.raises(ValueError):
        ferrypick.parse_link(f"{U}/fork/ca/rpms/python3.7/commits/rename")


def test_rename_git_diff_spec():
    line = b"diff --git a/python3.7.spec b/python3.7.spec"
    new = ferrypick.rename(line, "python3.7", "python37")
    assert new == b"diff --git a/python37.spec b/python37.spec"


def test_rename_git_diff_rpmlintrc():
    line = b"+++ b/python3.rpmlintrc"
    new = ferrypick.rename(line, "python3", "python3.9")
    assert new == b"+++ b/python3.9.rpmlintrc"


def test_rename_git_diff_random_occurrence():
    line = b" #  remember to update the python3-docs package as well"
    new = ferrypick.rename(line, "python3-docs", "python-docs")
    assert new == line


def test_patch_real():
    link = f"{U}/rpms/python3.9/c/a0928446.patch"
    original_name = "python3.9"
    current_name = "python3.8"
    expected = Path(__file__).parent / "a0928446.patch"
    with ferrypick.patch(link, original_name, current_name) as patch:
        assert Path(patch).read_text() == expected.read_text()
