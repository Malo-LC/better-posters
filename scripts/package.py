"""Package the plugin locally with JPRM, matching the CI release job.

JPRM shells out to `dotnet` and rewrites project metadata in place (version,
target framework). This wrapper restores those files afterwards so packaging
does not leave the working tree dirty.

It also prepends the mise-managed .NET SDK (exposed through DOTNET_ROOT) so
JPRM's `dotnet` calls win over any system-wide install that lacks an SDK.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

ARTIFACTS_DIR = pathlib.Path("artifacts")
# Files JPRM may rewrite while stamping version/framework.
MUTABLE_FILES = (
    pathlib.Path("Directory.Build.props"),
    pathlib.Path("BetterPosters/BetterPosters.csproj"),
    pathlib.Path("BetterPosters.Tests/BetterPosters.Tests.csproj"),
)


def build() -> int:
    """Run JPRM and return its exit code."""
    env = os.environ.copy()
    dotnet_root = env.get("DOTNET_ROOT")
    if dotnet_root:
        env["PATH"] = dotnet_root + os.pathsep + env.get("PATH", "")

    return subprocess.call(
        [
            "jprm",
            "plugin",
            "build",
            ".",
            "--output",
            str(ARTIFACTS_DIR),
            "--dotnet-configuration",
            "Release",
            "--dotnet-framework",
            "net9.0",
        ],
        env=env,
    )


def main() -> int:
    """Build the plugin zip into ./artifacts and restore project files."""
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    backups = {path: path.read_bytes() for path in MUTABLE_FILES if path.exists()}

    try:
        return build()
    finally:
        for path, content in backups.items():
            path.write_bytes(content)


if __name__ == "__main__":
    sys.exit(main())
