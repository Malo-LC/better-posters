# AGENTS.md

## Project Overview

- Better Posters is a Jellyfin plugin written in C# targeting `net10.0`. It registers a remote primary image provider for Movies and Series and builds poster URLs served by [btttr.cc](https://btttr.cc).
- This repository is a maintained hard fork of the archived [neurekadev/better-posters](https://github.com/neurekadev/better-posters). The default branch is `master`.
- Compatibility target: the latest Jellyfin 12.4.x release only. Jellyfin 10.11 and older are not supported. When bumping Jellyfin support, update the `Jellyfin.Controller`/`Jellyfin.Model` package versions, `build.yaml` `targetAbi` and `framework`, `mise.toml` `dotnet`, and the README minimum version together.

## Invariants

- Do not change the plugin GUID (`862b7dbc-9485-41f2-a9d9-fc9ca66a6a51`) or the configuration class/property names: existing installs must keep upgrading in place and keep their settings.
- Posters are only offered for items with an IMDb ID; btttr.cc URLs are IMDb-based by design.
- `BetterPosterUrlBuilder` is the single place that maps configuration to btttr.cc URLs. Keep it pure and covered by `BetterPosterUrlBuilderTests`.
- The configuration page is an embedded resource (`Configuration/configPage.html`); no frontend build step exists.

## Development Environment

- [mise](https://mise.jdx.dev/) is the source of truth for tool versions (`mise.toml`): .NET SDK, uv, and JPRM. Python is provisioned by uv, not installed as a mise tool. Do not document or script bare `dotnet`/`jprm`/`python`/`pip` invocations that bypass mise and uv.
- Use uv for every Python need: `uv run` for scripts, `uvx`/`uv tool` for CLI tools, and the `pypi:` mise backend for pinned tools. Do not use `pip`, `pipx`, or `setup-python`.
- First setup: `mise trust && mise install`.
- Tasks:
  - `mise run build` - build the plugin in Release.
  - `mise run test` - run the xUnit suite.
  - `mise run lint` - `dotnet format --verify-no-changes`.
  - `mise run package` - build `artifacts/better-posters_<version>.zip` through `scripts/package.py` (JPRM).
  - `mise run verify` - build, lint, test, then package, in that order. This must pass before considering a change done.
- CI installs every tool through `jdx/mise-action` from `mise.toml` (pinned by commit SHA with the release in a comment). Do not add `setup-dotnet`, `setup-python`, or `setup-uv` steps: bump versions in `mise.toml` only.
- A local smoke test can load the packaged plugin into `lscr.io/linuxserver/jellyfin:latest` (Jellyfin 12.4) and check the `Loaded plugin: Better Posters <version>` log line. See the README.

## Code Style

- Analyzers are strict: `TreatWarningsAsErrors`, `AnalysisMode=AllEnabledByDefault`, StyleCop, SerilogAnalyzer, and `jellyfin.ruleset`. Public members need XML documentation.
- Match the existing file-scoped namespace, nullable annotations, and collection-expression style.
- Do not hand-format generated output; run `mise run lint` instead.

## Release Metadata

- During release or `keep-a-changelog` work, keep `CHANGELOG.md` and `build.yaml` aligned.
- Use bare SemVer for tags and `CHANGELOG.md` headings, for example `1.2.3`.
- Use Jellyfin/JPRM four-part versions in `build.yaml` by appending `.0` to the release SemVer, for example `1.2.3` becomes `1.2.3.0`.
- Set `build.yaml` `changelog` to only the latest released changelog body, excluding older releases, `[Unreleased]`, and the release heading such as `## [1.2.3] - YYYY-MM-DD`.
- Markdown is allowed in `build.yaml` `changelog`; Jellyfin Web renders plugin revision changelogs as Markdown, and JPRM copies this field into the plugin manifest.
- Use a YAML literal block (`|`) for Markdown lists or multi-paragraph content, and a folded block (`>`) only for a single plain paragraph.
- Do not hand-edit `manifest.json` during release preparation unless explicitly requested; it is release output generated from package metadata.

## Release Pipeline

- Releases are published by GitHub Actions (`.github/workflows/CI.yml`) when a bare SemVer tag (for example `1.2.3`) is pushed. The workflow packages the plugin with JPRM, publishes a GitHub Release with the zip and checksums attached, and regenerates and commits `manifest.json` to the default branch.
- `CHANGELOG.md` must contain a released section matching the tag (`## [1.2.3] - ...`); the workflow reads it for the release notes and fails if it is missing.
- The release job uses the repository-scoped `GITHUB_TOKEN` with `contents: write`; no separate manifest token is required.
- README badges and install URLs, `build.yaml` `owner`/`imageUrl`, and the CHANGELOG compare links all point at the fork (`Malo-LC/better-posters`). The release workflow uses `GITHUB_REPOSITORY`, so releases and `manifest.json` updates always land on the repository that owns the tag.
