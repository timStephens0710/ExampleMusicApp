# Changelog

All notable changes to this project will be documented in this file.

# 2026-04-15
### Added
* Soundcloud as an accepted platform along with unit tests
* view_edit_playlist_mixes.html
* view_edit_playlist_tracks.html

### Changed
* Moved GetSoup to main_integrations.py as it can be used for other platforms that don't have APIs
* Display in view_edit_playlist_

# 2026-03-15
### Added
* User can delete playlist(s)
* User can delete track(s) from a playlist

# 2026-02-06
### Fixed
* Bandcamp bug via Selenium

### Changed
* Bandcamp API, we now scrape the HTML
* Added mocking to Integrations API test in order to make the run time more efficient.

### Added
* Unit tests for the updated Bandcamp API

# 2026-01-13
### Removed
* Unsupported streaming platforms from the models and forms to avoid confusion


# 2025-11-16
### Added
* Views to handle the archive
* Models for the archiving process
* urls for the archiving process
* Utils for the archiving process
* Services for the archiving process
* YouTube + Bandcamp API's
* Corresponding unit tests for:
    - Views
    - Models
    - Utils
    - Integrations
    - Services

