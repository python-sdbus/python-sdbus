# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2025 igo95862

# This file is part of python-sdbus

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Callable, Iterator
from functools import partial
from pathlib import Path
from subprocess import PIPE
from subprocess import run as _run

SDBUS_REFSPEC = "HEAD"
SDBUS_SRC_DIR = Path("/root/sdbus")

WHEEL_BUILD_DIR = Path(__file__).parent
PROJECT_ROOT = WHEEL_BUILD_DIR.parent
BUILD_DIR = PROJECT_ROOT / "build/wheel-build/"
LAST_STAGE_FILE = BUILD_DIR / "last_stage"

CONTAINER_IMAGE = "docker.io/debian:11-slim"
CONTAINER_NAME = "python-sdbus-build"
CONTAINER_ARCH = "x86_64"
DEBIAN_PACKAGES = (
    "python3",
    "python3-dev",
    "gcc", "gperf",
    "meson",
    "python3-wheel",
    "python-setuptools",
    "python3-jinja2",
    "libcap-dev",
    "libmount-dev",
    "git",
    "ca-certificates",
    "pkg-config",
)
DEBIAN_NAME = "bullseye"

BASIC_CFLAGS: list[str] = [
    '-O2', '-fno-plt', '-D_FORTIFY_SOURCE=2',
    '-fstack-clash-protection',
]

SYSTEMD_REPO = "https://github.com/systemd/systemd-stable.git"
# systemd 255 is last one before glibc 2.31 requirement
SYSTEMD_TAG = "v255.22"
SYSTEMD_SRC_DIR = Path("/root/systemd")
SYSTEMD_BUILD_DIR = SYSTEMD_SRC_DIR / "build"
SYSTEMD_COMPAT_PATCH_NAME = "systemd_no_gettid_no_getdents64.patch"
SYSTEMD_COMPAT_PATCH_FILE = WHEEL_BUILD_DIR / SYSTEMD_COMPAT_PATCH_NAME
SYSTEMD_OPTIONS: list[str] = [
    "static-libsystemd=pic",
    "tests=false",
    "coredump=false",
    "dbus=false",
    "efi=false",
    "elfutils=false",
    "hostnamed=false",
    "homed=false",
    "importd=false",
    "initrd=false",
    "kernel-install=false",
    "logind=false",
    "machined=false",
    "man=false",
    "networkd=false",
    "portabled=false",
    "repart=false",
    "sysext=false",
    "sysusers=false",
    "timedated=false",
    "timesyncd=false",
    "tmpfiles=false",
    "oomd=false",
    "hibernate=false",
    "nss-systemd=false",
    "nss-resolve=false",
]

run = partial(_run, check=True, cwd=PROJECT_ROOT)


def podman_exec(
    *args: str,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    input: bytes | None = None,
) -> None:

    env_list = [
        f"--env={env_k}={env_v}" for env_k, env_v in env.items()
    ] if env else []
    workdir_options = [f"--workdir={cwd}"] if cwd else []

    run(
        args=(
            "podman",
            "exec",
            *env_list,
            *workdir_options,
            "--tty" if input is None else "--interactive",
            CONTAINER_NAME,
            *args,
        ),
        input=input,
    )


def podman_cp(src: Path, dest: Path, to_contatiner: bool = True) -> None:
    if to_contatiner:
        src_str = str(src.absolute())
        dest_str = f"{CONTAINER_NAME}:{dest}"
    else:
        src_str = f"{CONTAINER_NAME}:{src}"
        dest_str = str(dest.absolute())

    run(
        args=("podman", "cp", src_str, dest_str)
    )


def podman_start() -> None:
    run(
        args=(
            "podman",
            "run",
            "--name", CONTAINER_NAME,
            "--arch", CONTAINER_ARCH,
            "--detach",
            "--rm", "--init",
            CONTAINER_IMAGE,
            "sleep", "3d",
        )
    )


def install_packages() -> None:
    target_release = ("--target-release", f"{DEBIAN_NAME}-backports")
    deb_env = {"DEBIAN_FRONTEND": "noninteractive"}
    podman_exec(
        "bash",
        "-c",
        "echo 'deb http://archive.debian.org/debian "
        f"{DEBIAN_NAME}-backports main'"
        " > /etc/apt/sources.list.d/backports.list"
    )
    podman_exec("apt-get", "update", env=deb_env)
    podman_exec(
        "apt-get",
        "upgrade",
        *target_release,
        "--yes",
        env=deb_env,
    )
    podman_exec(
        "apt-get",
        "install",
        *target_release,
        "--yes",
        "--no-install-recommends",
        *DEBIAN_PACKAGES,
        env=deb_env,
    )


def clone_systemd() -> None:
    podman_exec(
        "git", "clone",
        "--depth", "1",
        "--branch", SYSTEMD_TAG,
        "--",
        SYSTEMD_REPO,
        str(SYSTEMD_SRC_DIR),
    )


def apply_systemd_patch() -> None:
    podman_cp(SYSTEMD_COMPAT_PATCH_FILE, SYSTEMD_SRC_DIR)
    podman_exec(
        "git", "apply", SYSTEMD_COMPAT_PATCH_NAME,
        cwd=SYSTEMD_SRC_DIR,
    )


def build_systemd() -> None:
    systemd_options_get = (f"-D{o}" for o in SYSTEMD_OPTIONS)
    cflags = {"CFLAGS": " ".join(BASIC_CFLAGS)}
    podman_exec(
        "meson",
        "setup",
        "--auto-features=disabled",
        "--buildtype=release",
        *systemd_options_get,
        str(SYSTEMD_BUILD_DIR),
        cwd=SYSTEMD_SRC_DIR,
        env=cflags,
    )
    podman_exec(
        "meson",
        "compile",
        "systemd:static_library",
        "libsystemd.pc",
        cwd=SYSTEMD_BUILD_DIR,
    )


def install_systemd_files() -> None:
    podman_exec(
        "bash",
        "-c",
        "cp libsystemd.a"
        " /usr/lib/$(cat /usr/lib/pkg-config.multiarch)/",
        cwd=SYSTEMD_BUILD_DIR,
    )
    podman_exec(
        "cp",
        "src/libsystemd/libsystemd.pc",
        "/usr/share/pkgconfig/",
        cwd=SYSTEMD_BUILD_DIR,
    )
    podman_exec(
        "cp",
        "src/libsystemd/libsystemd.pc",
        "/usr/share/pkgconfig/",
        cwd=SYSTEMD_BUILD_DIR,
    )
    podman_exec(
        "mkdir", "--parents", "/usr/include/systemd/"
    )
    required_headers = (
        "_sd-common.h",
        "sd-id128.h",
        "sd-daemon.h",
        "sd-bus.h",
        "sd-bus-vtable.h",
        "sd-bus-protocol.h",
        "sd-device.h",
        "sd-event.h",
    )
    podman_exec(
        "cp",
        *(f"src/systemd/{h}" for h in required_headers),
        "/usr/include/systemd/",
        cwd=SYSTEMD_SRC_DIR,
    )


def copy_sdbus_sources() -> None:
    podman_exec("mkdir", "--parents", str(SDBUS_SRC_DIR))
    sdbus_tar = run(
        args=("git", "archive", SDBUS_REFSPEC),
        stdout=PIPE,
    ).stdout
    assert isinstance(sdbus_tar, bytes)
    print("python-sdbus source archive size:", len(sdbus_tar))
    podman_exec(
        "tar", "--extract", "--verbose",
        cwd=SDBUS_SRC_DIR,
        input=sdbus_tar,
    )


def compile_sdbus() -> None:
    podman_exec(
        "python3", "setup.py", "build", "bdist_wheel",
        "--py-limited-api", "cp39",
        cwd=SDBUS_SRC_DIR,
        env={
            "PYTHON_SDBUS_USE_STATIC_LINK": "1",
            "PYTHON_SDBUS_USE_LIMITED_API": "1",
            "CFLAGS": " ".join(BASIC_CFLAGS),
        },
    )


def copy_dist() -> None:
    podman_cp(
        SDBUS_SRC_DIR / "dist",
        BUILD_DIR / f"{CONTAINER_ARCH}-dist",
        to_contatiner=False,
    )


STAGES: dict[str, Callable[[], None]] = {
    "podman_start": podman_start,
    "install_packages": install_packages,
    "clone_systemd": clone_systemd,
    "apply_systemd_patch": apply_systemd_patch,
    "build_systemd": build_systemd,
    "install_systemd_files": install_systemd_files,
    "copy_sdbus_sources": copy_sdbus_sources,
    "compile_sdbus": compile_sdbus,
    "copy_dist": copy_dist,
}


def iter_stages() -> Iterator[tuple[str, Callable[[], None]]]:
    stages_iter = iter(STAGES.items())
    if LAST_STAGE_FILE.exists():
        last_stage = LAST_STAGE_FILE.read_text().strip()
        for stage_name, _ in stages_iter:
            if stage_name == last_stage:
                print("Last completed stage:", stage_name)
                break
            else:
                print("Skipping stage:", stage_name)

    yield from stages_iter


def main() -> None:
    args_parser = ArgumentParser()
    args_parser.add_argument("--arch")
    args = args_parser.parse_args()

    if arch := args.arch:
        global CONTAINER_ARCH
        CONTAINER_ARCH = arch

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    for stage_name, stage_func in iter_stages():
        stage_func()
        LAST_STAGE_FILE.write_text(stage_name)
        print("Completed:", stage_name)


if __name__ == "__main__":
    main()
