<div align="center">

<img src="Assets/Logo.png" alt="Logo" height="128px" />

# Better Posters

[![Release](https://img.shields.io/github/v/release/Malo-LC/better-posters?style=flat-square&logo=github&logoColor=F43F5E&label=Release&color=F43F5E)](https://github.com/Malo-LC/better-posters/releases/latest)
[![Pipeline](https://img.shields.io/github/actions/workflow/status/Malo-LC/better-posters/CI.yml?branch=master&style=flat-square&logo=githubactions&logoColor=8B5CF6&label=Pipeline&color=8B5CF6)](https://github.com/Malo-LC/better-posters/actions/workflows/CI.yml)
[![License](https://img.shields.io/github/license/Malo-LC/better-posters?style=flat-square&label=License&color=14B8A6&logo=opensourceinitiative&logoColor=14B8A6)](./LICENSE.md)
[![Stars](https://img.shields.io/github/stars/Malo-LC/better-posters?style=flat-square&label=Stars&color=EAB308&logo=googlegemini&logoColor=EAB308)](https://github.com/Malo-LC/better-posters)

**Better Posters** is an unofficial Jellyfin plugin that lets you replace standard movie and show posters with customizable posters from [btttr.cc](https://btttr.cc).

</div>

**Minimum Jellyfin version:** 12.4

> **Maintained fork.** This repository is a hard fork of the archived [neurekadev/better-posters](https://github.com/neurekadev/better-posters). It keeps the original plugin GUID and configuration format, and is maintained against the latest Jellyfin 12.4.x release. Jellyfin 10.11 and older are no longer supported.

## Features

- **Movies and Shows:** Registers as a remote primary image provider for movie and series items.
- **Configurable Poster Overlays:** Toggle trend tags, quality badges, genre, rating, and age rating.
- **Rating Source Selection:** Use btttr.cc average ratings or choose IMDb, TMDB, Rotten Tomatoes, Metacritic, Trakt, Letterboxd, or Roger Ebert.
- **Multi-Language Posters:** Select English, Spanish, French, German, Portuguese, Italian, Dutch, Polish, Russian, Turkish, Arabic, Japanese, Korean, Chinese, Hindi, Swedish, or Czech.
- **Scheduled Replacement:** Optionally replace existing movie and show posters through Jellyfin Scheduled Tasks.

## Installation Guide

### Option 1: Install from the Plugin Repository

1. Open **Dashboard -> Plugins -> Repositories** in Jellyfin.
2. Add this repository URL:

    ```text
    https://raw.githubusercontent.com/Malo-LC/better-posters/master/manifest.json
    ```

3. Open **Dashboard -> Plugins -> Catalog**.
4. Select **Better Posters** and install the latest compatible version.
5. Restart Jellyfin.
6. Confirm **Better Posters** appears under **Dashboard -> Plugins -> My Plugins**.

### Option 2: Install Manually from a Release

1. Download the latest `better-posters_*.zip` asset from the [GitHub releases page](https://github.com/Malo-LC/better-posters/releases/latest).
2. Stop Jellyfin.
3. Create a Better Posters plugin folder under your Jellyfin plugins directory.
4. Extract the release zip into that folder.
5. Start Jellyfin.
6. Confirm **Better Posters** appears under **Dashboard -> Plugins -> My Plugins**.

### Option 3: Build from Source

Development tooling is managed by [mise](https://mise.jdx.dev/). Install mise, then from this repository:

```shell
mise trust
mise install
mise run package
```

The plugin zip is written to `artifacts/better-posters_<version>.zip`. Extract it into a Better Posters plugin folder under your Jellyfin plugins directory and restart Jellyfin.

The plugin targets Jellyfin 12.4 and will not load on Jellyfin 10.11 or older.

## Configuration & Setup

Open **Dashboard -> Plugins -> My Plugins -> Better Posters**.

Default settings:

- **Trend Tags:** Enabled
- **Quality Tags:** Disabled
- **Genre:** Enabled
- **Ratings:** Enabled
- **Ratings Source:** Average
- **Age Rating:** Disabled
- **Language:** English

The **Update Better Posters** scheduled task is unscheduled by default. Configure it under **Dashboard -> Scheduled Tasks** to replace existing primary posters for Movies and Shows that have an IMDb ID.

## How to Apply Posters to Your Library

### Option A: Apply to a Single Movie or Show

1. Open a Movie or Show in Jellyfin.
2. Select **Edit Images**.
3. Search remote images.
4. Choose the Better Posters primary image.

### Option B: Apply During Metadata Refresh

1. Go to **Dashboard -> Libraries**.
2. Open the menu for a Movies or Shows library.
3. Select **Scan Library**.
4. Choose metadata refresh options that replace existing images.

### Option C: Apply Automatically

1. Open **Dashboard -> Scheduled Tasks**.
2. Select **Update Better Posters**.
3. Add the schedule you want Jellyfin to use.
4. The scheduled task will replace matching movie and show primary images using the current poster settings.

## How It Works

The plugin is a thin adapter between Jellyfin and btttr.cc:

1. `BetterPostersImageProvider` is registered as a Jellyfin remote image provider. For Movies and Series that have an IMDb ID, it advertises exactly one remote primary image.
2. `BetterPosterUrlBuilder` turns the plugin configuration into a btttr.cc URL:

    ```text
    https://btttr.cc/{poster-path}/imdb/poster-default/{imdbId}.jpg?tag=none&lang=fr&rs=IM
    ```

    - `poster-path` combines the genre/rating variant (`poster`, `poster-g`, `poster-r`, `poster-n`) with optional `q` (quality tags) and `a` (age rating) suffixes.
    - `tag=none` is sent only when trend tags are disabled.
    - `lang` is sent only for non-English languages.
    - `rs` is sent only when ratings are enabled and the rating source is not the btttr.cc average.

3. `BetterPostersUpdateTask` is an optional scheduled task. It walks every Movie and Series with an IMDb ID, skips items where Better Posters is not enabled as an image fetcher for the library, downloads the configured poster, and replaces the primary image.

### Project Layout

| Path | Responsibility |
| --- | --- |
| `BetterPosters/Plugin.cs` | Plugin entry point, GUID, embedded configuration page. |
| `BetterPosters/PluginServiceRegistrator.cs` | Registers the image provider and the scheduled task in Jellyfin's DI container. |
| `BetterPosters/Providers/BetterPostersImageProvider.cs` | Implements `IRemoteImageProvider` for Movies and Series. |
| `BetterPosters/BetterPosterUrlBuilder.cs` | Maps configuration to btttr.cc URLs (pure, unit-tested). |
| `BetterPosters/ScheduledTasks/BetterPostersUpdateTask.cs` | Bulk poster replacement task. |
| `BetterPosters/Configuration/PluginConfiguration.cs` | Serializable plugin settings and enums. |
| `BetterPosters/Configuration/configPage.html` | Embedded Jellyfin Web configuration page. |
| `BetterPosters.Tests/` | xUnit tests for URL building and task behavior. |

## Development

### Prerequisites

Only [mise](https://mise.jdx.dev/) is required. `mise.toml` pins the .NET SDK, [uv](https://docs.astral.sh/uv/), and JPRM versions used locally and by CI. Python itself is provisioned by uv, not by mise.

```shell
mise trust
mise install
```

If your shell is not already configured for mise, add `mise activate <shell>` to your shell profile or prefix commands with `mise exec --`.

### Common Tasks

| Command | Description |
| --- | --- |
| `mise run build` | Build the plugin in Release. |
| `mise run test` | Run the xUnit test suite. |
| `mise run lint` | Verify formatting and analyzer rules without modifying files. |
| `mise run package` | Build the Jellyfin plugin zip into `artifacts/`. |
| `mise run verify` | Run build, lint, test, and package sequentially. |

### Smoke Test with Jellyfin

The plugin can be loaded in a throwaway Jellyfin container to confirm it starts:

```powershell
mise run package

$plugin = "$PWD\artifacts\plugin"
Expand-Archive artifacts\better-posters_*.zip -DestinationPath $plugin -Force

docker run -d --name jf-better-posters -p 8097:8096 `
  -e PUID=1000 -e PGID=1000 -e TZ=Etc/UTC `
  --mount "type=bind,source=$plugin,target=/config/data/plugins/BetterPosters" `
  lscr.io/linuxserver/jellyfin:latest

docker logs jf-better-posters 2>&1 | Select-String "Better Posters"
```

`lscr.io/linuxserver/jellyfin:latest` tracks the latest stable Jellyfin release (12.4 at the time of writing). Pin `version-12.4ubu2604` to stay on that exact build. The linuxserver image keeps Jellyfin data under `/config/data`, so plugins belong in `/config/data/plugins`.

A healthy startup logs:

```text
Loaded plugin: Better Posters <version>
```

Then open `http://localhost:8097` to complete the Jellyfin setup wizard. Clean up with:

```shell
docker rm -f jf-better-posters
```

### Release

Releases are published by GitHub Actions when a bare SemVer tag is pushed:

```shell
git tag 1.2.3
git push origin 1.2.3
```

Before tagging, align `CHANGELOG.md` and `build.yaml` (see `AGENTS.md`).

## Troubleshooting

- **No Better Posters image appears:** Confirm the item has an IMDb ID. This plugin intentionally uses IMDb IDs for btttr.cc URLs.
- **Plugin does not load:** Confirm the server is Jellyfin 12.4 or newer and restart Jellyfin after copying the plugin DLL. Plugins built for Jellyfin 10.11 will not load on Jellyfin 12.
- **Poster did not change after selecting one:** Clear the browser cache or check another Jellyfin client. Jellyfin and browsers can cache images aggressively.

## Disclaimer

This is an unofficial Jellyfin plugin. Poster artwork and generated image output are provided by [btttr.cc](https://btttr.cc).
