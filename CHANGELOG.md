# Changelog — Project Volusia

> All notable changes to Project Volusia.

---

## [Unreleased] - 2026-09-08

### Added
- New data pipeline v6 with improved quality validation
- Data quality standards documentation
- Troubleshooting guide
- FAQ documentation
- Security documentation
- Frontend documentation
- Connection guide between repos

### Changed
- Improved category normalization (Economy → Economic)
- Enhanced bad value detection (Census null markers)
- Updated API endpoints documentation
- Restructured documentation directory

### Removed
- Broken gamification system (was causing build failures)
- Duplicate CVB hotel records
- Duplicate climate indicators

### Fixed
- TypeScript build errors in all page components
- CORS configuration for API access
- GitHub Actions deployment workflow

---

## [2.0.0] - 2026-09-05

### Added
- Real data pipeline (Census, BLS, BEA, NOAA)
- 26 high-quality indicators across 4 categories
- JSON export for static hosting
- GitHub Pages deployment
- React/TypeScript frontend with Vite
- Nivo charts integration
- Leaflet maps integration
- Tailwind CSS styling

### Changed
- Migrated from sample data to live government APIs
- Replaced static sampleData.ts with dynamic hooks
- Updated routing to React Router v6

---

## [1.0.0] - 2026-09-03

### Added
- Initial project structure
- FastAPI backend with SQLite
- Sample data for development
- Basic HTML portal
- Docker support
- Documentation framework

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
