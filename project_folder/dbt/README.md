# Music App — dbt Project

This directory contains the dbt project for the Music App data analytics layer. It transforms raw data extracted from the Django/PostgreSQL application into clean, tested, and business-ready models inside Snowflake.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Models](#models)
  - [Staging](#staging)
  - [Marts](#marts)
- [Data Quality Tests](#data-quality-tests)
- [Snowflake Setup](#snowflake-setup)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Naming Conventions](#naming-conventions)
- [Roadmap](#roadmap)

---

## Overview

The dbt project sits at the transformation layer of the Music App modern data stack:

```
Django App (PostgreSQL)
        │
        │  Airflow extracts & loads
        ▼
   Snowflake RAW          ← raw source data, never modified
        │
        │  dbt transforms
        ▼
   Snowflake STAGING      ← cleaned & standardised models
        │
        │  dbt transforms
        ▼
   Snowflake MARTS        ← business-ready analytical models
```

dbt is responsible for everything **inside** Snowflake. Loading raw data from PostgreSQL into the `RAW` schema is handled by Airflow (see pipeline orchestration section).

---

## Architecture

This project follows the **medallion architecture** pattern — a standard approach in data engineering that separates data by quality and transformation level:

| Layer | Schema | Purpose |
|---|---|---|
| Raw | `RAW` | Data as-is from the source. Never modified. Single source of truth. |
| Staging | `STAGING` | Cleaned, renamed, typed, and deduplicated. One model per source table. |
| Marts | `MARTS` | Business-ready models that answer analytical questions. |

---

## Project Structure

```
dbt/
├── models/
│   ├── staging/                    # One model per source table
│   │   ├── stg_tracks.sql
│   │   ├── stg_playlists.sql
│   │   ├── stg_streaming_links.sql
│   │   ├── stg_users.sql
│   │   └── _staging.yml            # Staging model documentation & tests
│   └── marts/                      # Business-ready analytical models
│       ├── most_played_artists.sql
│       ├── playlist_growth.sql
│       ├── platform_breakdown.sql
│       └── _marts.yml              # Mart model documentation & tests
├── tests/                          # Custom singular tests
├── macros/                         # Reusable SQL macros
├── seeds/                          # Static reference data (CSV)
├── snapshots/                      # Slowly changing dimension tracking
├── dbt_project.yml                 # Project configuration
└── README.md                       # This file
```

---

## Models

### Staging

Staging models clean and standardise the raw source data. Each model maps 1:1 to a source table in the `RAW` schema. Transformations at this layer are limited to:

- Renaming columns to `snake_case`
- Casting data types (e.g. strings to timestamps)
- Deduplicating records
- Filtering out soft-deleted rows
- Basic `null` handling

| Model | Source Table | Description |
|---|---|---|
| `stg_tracks` | `RAW.tracks` | Music tracks with metadata (title, artist, album) |
| `stg_playlists` | `RAW.playlists` | User playlists with privacy settings |
| `stg_streaming_links` | `RAW.streaming_links` | Platform URLs linked to tracks |
| `stg_users` | `RAW.users` | App users (anonymised where necessary) |

### Marts

Mart models join and aggregate staging models to produce business-ready outputs. These are the tables used for analysis and reporting.

| Model | Description |
|---|---|
| `most_posted_artists` | Artist frequency ranked by number of tracks saved |
| `playlist_growth` | Playlist creation and track addition over time |
| `platform_breakdown` | Track counts broken down by streaming platform |

---

## Data Quality Tests

dbt's built-in testing framework is used across all models to ensure data integrity. Tests are defined in the `.yml` schema files alongside each model.

### Generic Tests (applied via `.yml`)

```yaml
# Example: _staging.yml
models:
  - name: stg_tracks
    columns:
      - name: track_id
        tests:
          - not_null
          - unique
      - name: artist
        tests:
          - not_null
      - name: streaming_platform
        tests:
          - accepted_values:
              values: ['youtube', 'youtube_music', 'bandcamp']
```

### Running Tests

```bash
# Run all tests
dbt test

# Run tests for a specific model
dbt test --select stg_tracks

# Run tests for a specific layer
dbt test --select staging
```

---

## Snowflake Setup

The dbt project connects to Snowflake using the following resources:

| Resource | Value |
|---|---|
| Database | `MUSIC_APP_DB` |
| Warehouse | `MUSIC_APP_WH` |
| Role | `MUSIC_APP_ROLE` |
| Production schema (staging models) | `STAGING` |
| Production schema (mart models) | `MARTS` |
| Development schema | `dbt_<your_name>` |

The full Snowflake setup SQL is located in the root of the repository at `snowflake_setup.sql`.

---

## Getting Started

### Prerequisites

- A [dbt Cloud](https://cloud.getdbt.com) account
- Access to the Snowflake `MUSIC_APP_DB` database with `MUSIC_APP_ROLE`
- Access to this GitHub repository

### dbt Cloud Setup

1. Log in to [dbt Cloud](https://cloud.getdbt.com)
2. Navigate to **Account Settings → Connections** and verify the Snowflake connection is configured
3. Go to **Develop → Studio** and ensure the DEV environment is pointing to this repository's `/dbt` subdirectory
4. Set your **development credentials** (Snowflake username & password) in your profile settings

### Running Models Locally (dbt Core)

If using dbt Core instead of dbt Cloud:

```bash
# Install dbt with Snowflake adapter
pip install dbt-snowflake

# Verify connection
dbt debug

# Run all models
dbt run

# Run a specific model
dbt run --select stg_tracks

# Run a layer
dbt run --select staging
dbt run --select marts
```

---

## Development Workflow

This project follows a Git-based development workflow:

```
1. Create a feature branch
   git checkout -b feature/add-stg-tracks

2. Build and test your model in the dbt Cloud IDE
   dbt run --select stg_tracks
   dbt test --select stg_tracks

3. Commit changes
   git commit -m "feat: add stg_tracks staging model"

4. Open a Pull Request → merge to main

5. Production run triggered via Airflow (or dbt Cloud scheduler)
```

### Branch Naming

```
feature/add-<model-name>     # New models
fix/fix-<model-name>         # Bug fixes
refactor/<model-name>        # Refactoring existing models
```

---

## Naming Conventions

| Layer | Prefix | Example |
|---|---|---|
| Staging | `stg_` | `stg_tracks` |
| Intermediate | `int_` | `int_tracks_with_platforms` |
| Marts | No prefix | `most_played_artists` |

**Column naming:**
- All columns in `snake_case`
- Primary keys named `<model>_id` (e.g. `track_id`)
- Timestamps suffixed `_at` (e.g. `created_at`)
- Boolean columns prefixed `is_` or `has_` (e.g. `is_public`)

---

## Roadmap

- [x] Snowflake warehouse and schema setup
- [x] dbt Cloud connected to Snowflake and GitHub
- [x] dbt project initialised
- [ ] Load source data into `RAW` schema via Airflow
- [ ] Build staging models (tracks, playlists, streaming links, users)
- [ ] Build mart models (most played artists, playlist growth, platform breakdown)
- [ ] Add data quality tests to all models
- [ ] Add dbt model documentation and column descriptions
- [ ] Configure dbt Cloud production job
- [ ] Wire up Airflow DAG to trigger dbt runs on schedule

---

**Maintained by:** Tim Stephens
**Last Updated:** February 2026
**dbt Version:** Latest (managed via dbt Cloud)
**Snowflake Database:** `MUSIC_APP_DB`
