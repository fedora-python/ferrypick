#!/usr/bin/env python3

import os.path
import re
import subprocess
import sys
import urllib.request

COMMIT_RE = re.compile(r"^https://src\.fedoraproject\.org/\S+/([^/\s]+)/c/([0-9a-f]+)")
PR_RE = re.compile(r"^https://src\.fedoraproject\.org/\S+/([^/\s]+)/pull-request/\d+")
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/#_common_character_set_for_package_naming
PKGNAME_RE = r"[a-zA-Z0-9_.+-]+"
# Files named pkgname.spec and pkgname.rpmlintrc need to be renamed in patches
SUFFIXES_RE = r"\.(spec|rpmlintrc)"
# This is what git does: "a" in "a/python37.spec"
PREFIXES_RE = r"(a|b)"
RENAME_RE_TEMPLATE = f"(?P<prefix>{PREFIXES_RE})/{{}}(?P<suffix>{SUFFIXES_RE})"


def parse_link(link):
    """
    For a given pagure link, return package name and the patch link.
    Raise ValueError if not recognized.
    """
    for regex in COMMIT_RE, PR_RE:
        if match := regex.match(link):
            return match.group(1), match.group(0) + ".patch"
    raise ValueError("Unrecognized link")


def rename(content, original_name, current_name):
    """
    In a given bytes patch-content, replace original package name with current package name.
    If original_name is None, it replaces a more general regular expression instead.
    Works on pkgname.spec and pkgname.rpmlintrc only (as defined in SUFFIXES).
    """
    if original_name is not None and original_name == current_name:
        return content

    def replace(regs):
        prefix = regs.group("prefix")
        new_name = current_name.encode("utf8")
        suffix = regs.group("suffix")
        return b"%s/%s%s" % (prefix, new_name, suffix)

    if original_name is not None:
        name_regex = re.escape(original_name)
    else:
        name_regex = PKGNAME_RE
    regex = RENAME_RE_TEMPLATE.format(name_regex)
    regex = regex.encode("utf-8")
    content = re.sub(regex, replace, content)
    return content


def download(link):
    print(f"Downloading {link}")
    with urllib.request.urlopen(link) as response:
        content = response.read()
    return content


def stdout(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).rstrip()


def execute(cmd):
    proc = subprocess.run(cmd, shell=True, text=True)
    return proc.returncode


def parse_args():
    # TODO?: Add more sophisticated argument parsing
    if len(sys.argv) < 2:
        for arg in ("COMMIT", "PR_LINK", "FILENAME"):
            print(f"Usage: {sys.argv[0]} {arg} [CURRENT_PKGNAME]")
        sys.exit(1)

    link = sys.argv[1]
    try:
        current_name = sys.argv[2]
    except IndexError:
        git_toplevel = stdout("git rev-parse --show-toplevel")
        current_name = os.path.basename(git_toplevel)

    return (link, current_name)


def get_patch_content(link):
    if os.path.exists(link):
        with open(link, "rb") as fp:
            content = fp.read()
        original_name = None
    else:
        original_name, patch_link = parse_link(link)
        content = download(patch_link)
    return (content, original_name)


def apply_patch(filename):
    cmd = f"git am --reject {filename}"
    print(f"$ {cmd}")
    exitcode = execute(cmd)
    if exitcode:
        print(file=sys.stderr)
        print(f"{cmd} failed with exit code {exitcode}", file=sys.stderr)
        print(f"Patch stored as: {filename}", file=sys.stderr)
        sys.exit(exitcode)


def main():
    link, current_name = parse_args()
    content, original_name = get_patch_content(link)
    content = rename(content, original_name, current_name)

    filename = "ferrypick.patch"
    with open(filename, "wb") as fp:
        fp.write(content)
        fp.flush()

    apply_patch(filename)
    os.unlink(filename)


if __name__ == "__main__":
    main()
