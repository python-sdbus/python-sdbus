# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: 2024 igo95862
from __future__ import annotations

from argparse import ArgumentParser
from unittest.mock import patch

from auditwheel.main import main as auditwheel_main  # type: ignore


def main(arch: str, wrapped_args: list[str]) -> None:
    with patch("sys.argv", [""] + wrapped_args), patch(
        "platform.machine", return_value=arch
    ):
        auditwheel_main()


if __name__ == "__main__":
    arg_parse = ArgumentParser()
    arg_parse.add_argument(
        "--arch",
        choices=("x86_64", "i686", "aarch64", "armv7l"),
        default="x86_64",
    )
    arg_parse.add_argument("wrapped_args", nargs="*")

    main(**vars(arg_parse.parse_args()))
