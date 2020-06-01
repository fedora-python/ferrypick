ferrypicker
===========

Apply patches from Fedora dist git to different components.

This simple tool does 3 steps:

 1. download patch file from src.fedoraproject.org
 2. replaces package name with current dist-git work dir package name
 3. runs `git am --reject` on the product

Usage:

```shell
[python36 (f32 %)]$ git switch -c f32-backport
Switched to a new branch 'f32-backport'

[python36 (f32-backport %)]$ ferrypick https://src.fedoraproject.org/rpms/python3.6/pull-request/2
Downloading https://src.fedoraproject.org/rpms/python3.6/pull-request/2.patch
$ git am --reject /tmp/tmp7pa062j6.patch
Applying: Fix python3-config --configdir
Checking patch 00102-lib64.patch...
.git/rebase-apply/patch:26: new blank line at EOF.
+
Checking patch 00205-make-libpl-respect-lib64.patch...
Checking patch python36.spec...
error: while searching for:
#global prerel ...
%global upstream_version %{general_version}%{?prerel}
Version: %{general_version}%{?prerel:~%{prerel}}
Release: 4%{?dist}
License: Python



error: patch failed: python36.spec:17
error: while searching for:
# ======================================================

%changelog
* Wed May 06 2020 Miro Hrončok <mhroncok@redhat.com> - 3.6.10-4
- Rename from python36 to python3.6


error: patch failed: python36.spec:1535
Applied patch 00102-lib64.patch cleanly.
Applied patch 00205-make-libpl-respect-lib64.patch cleanly.
Applying patch python36.spec with 2 rejects...
Rejected hunk #1.
Hunk #2 applied cleanly.
Hunk #3 applied cleanly.
Rejected hunk #4.
Patch failed at 0001 Fix python3-config --configdir
hint: Use 'git am --show-current-patch=diff' to see the failed patch
When you have resolved this problem, run "git am --continue".
If you prefer to skip this patch, run "git am --skip" instead.
To restore the original branch and stop patching, run "git am --abort".
```

Enjoy.
