import sys
import pytest
from pathlib import Path
from unittest import mock

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


def test_functional():
    # only mock download() and apply_patch()

    link = f"{U}/rpms/python3.9/c/a0928446.patch"
    current_name = "python3.8"
    download_content = (Path(__file__).parent / "a0928446.patch").read_bytes()
    expected = (Path(__file__).parent / "a0928446_py38.patch").read_bytes()
    argv = [sys.argv[0], link, current_name]
    apply_content = None

    def apply_patch(filename):
        nonlocal apply_content
        with open(filename, "rb") as fp:
            apply_content = fp.read()

    with mock.patch("sys.argv", argv), mock.patch.object(
        ferrypick, "download", return_value=download_content
    ), mock.patch.object(ferrypick, "apply_patch", apply_patch):
        ferrypick.main()

    assert apply_content == expected
