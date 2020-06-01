import contextlib
import os.path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

COMMIT_RE = re.compile(r"^https://src\.fedoraproject\.org/\S+/([^/\s]+)/c/([0-9a-f]+)")
PR_RE = re.compile(r"^https://src\.fedoraproject\.org/\S+/([^/\s]+)/pull-request/\d+")
REPLACE_SUFFIXES = "spec", "rpmlintrc"


def parse_link(link):
    """
    For a given pagure link, return package name and the patch link.
    Raise ValueError if not recognized.
    """
    for regex in COMMIT_RE, PR_RE:
        if match := regex.match(link):
            return match.group(1), match.group(0) + ".patch"
    raise ValueError("Unrecognized link")


def rename(bytesline, original_name, current_name):
    """
    On a given bytes line, naïvely replace original package name with current package name.
    Works on pkgname.spec and pkgname.rpmlintrc only (as defined in REPLACE_SUFFIXES).
    """
    if original_name != current_name:
        for suffix in REPLACE_SUFFIXES:
            for prefix in "a", "b":  # this is what git does
                original = f"{prefix}/{original_name}.{suffix}".encode("utf-8")
                current = f"{prefix}/{current_name}.{suffix}".encode("utf-8")
                bytesline = bytesline.replace(original, current)
    return bytesline


@contextlib.contextmanager
def patch(link, original_name, current_name):
    print(f"Downloading {link}")
    with tempfile.NamedTemporaryFile(suffix=".patch") as tmp_file:
        with urllib.request.urlopen(link) as response:
            for line in response:
                tmp_file.write(rename(line, original_name, current_name))
            tmp_file.flush()
        yield tmp_file.name


def stdout(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).rstrip()


def execute(cmd):
    return subprocess.run(cmd, shell=True, text=True)


def main():
    # TODO?: Add more sophisticated argument parsing
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} COMMIT_OR_PR_LINK [CURRENT_PKGNAME]")
    link = sys.argv[1]
    try:
        current_name = sys.argv[2]
    except IndexError:
        current_name = os.path.basename(stdout("git rev-parse --show-toplevel"))

    original_name, patch_link = parse_link(link)
    with patch(patch_link, original_name, current_name) as p:
        print(f"$ git am --reject {p}")
        execute(f"git am --reject {p}")


if __name__ == "__main__":
    main()
