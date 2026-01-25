# Changelog

All notable changes to the dev-tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add `/dev-tools:analyze-codebase` command for comprehensive codebase analysis
- Add `codebase-analyzer` agent (Opus) for deep architecture and pattern analysis
- Add `report-generator` agent (Sonnet) for generating polished markdown reports
- Add 3-phase workflow: exploration, analysis, report generation

## [0.2.2] - 2026-01-22

### Fixed

- Fix feature-dev workflow stopping prematurely after Phase 5 (Implementation) by adding explicit continuation directives to proceed through Phase 6 (Quality Review) and Phase 7 (Summary)

## [0.2.1] - 2026-01-21

### Added

- Add argument-hint to git-workflow skill triggers

### Changed

- Improve git-workflow trigger phrases for better matching

## [0.2.0] - 2026-01-20

### Added

- Initial release with feature-dev workflow
- Git commit and push commands
- Code exploration, architecture, and review agents
- Release automation for Python packages
- Plugin version bumping command
