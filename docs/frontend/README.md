# Frontend Documentation — Project Volusia

> Frontend-specific documentation for developers working on the React/TypeScript portal.

---

## Overview

The frontend is a React 18 + TypeScript application built with Vite, Tailwind CSS, Nivo charts, and Leaflet maps. It's deployed to GitHub Pages and uses static JSON files from the backend.

---

## Tech Stack

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.3.1 | UI framework |
| react-dom | ^18.3.1 | DOM rendering |
| react-router-dom | ^6.27.0 | Client-side routing |
| vite | ^5.4.9 | Build tool |
| typescript | ^5.6.3 | Type safety |
| tailwindcss | ^3.4.13 | Utility-first CSS |
| @nivo/line | ^0.87.0 | Line charts |
| @nivo/bar | ^0.87.0 | Bar charts |
| @nivo/pie | ^0.87.0 | Pie charts |
| @nivo/geo | ^0.87.0 | Geo maps |
| leaflet | ^1.9.4 | Interactive maps |
| react-leaflet | ^4.2.1 | React wrapper for Leaflet |
| axios | ^1.7.7 | HTTP client |
| date-fns | ^4.1.0 | Date utilities |

---

## Project Structure

```
src/
├── App.tsx                    # Main app component
├── main.tsx                   # Entry point
├── index.css                  # Global styles
├── components/
│   ├── Layout.tsx             # Header, Footer, Navigation
│   └── UI.tsx                 # Reusable UI components
├── hooks/
│   └── useApi.ts              # Data fetching hooks
├── pages/
│   ├── HomePage.tsx           # Landing page
│   ├── DataExplorerPage.tsx   # Data search/filter
│   ├── MapsPage.tsx           # Interactive map
│   ├── BusinessPage.tsx       # Business dashboard
│   ├── ResidentsPage.tsx      # Resident data
│   ├── TouristsPage.tsx       # Tourism data
│   ├── LeadersPage.tsx        # Investor data
│   └── NewsPage.tsx           # News/updates
└── types/
    └── index.ts               # TypeScript interfaces
```

---

## Components

### Layout.tsx

Main application layout with header, navigation, and footer.

**Props**: None (uses React Router for page routing)

**State**:
- `mobileOpen` — Mobile menu toggle

### UI.tsx

Reusable UI components:

| Component | Props | Description |
|-----------|-------|-------------|
| `StatCard` | `value`, `label`, `change`, `changeLabel` | KPI display card |
| `Card` | `children`, `className`, `hover` | Container card |
| `SectionTitle` | `title`, `subtitle` | Section heading |
| `Badge` | `children`, `variant` | Status badge |
| `DataSource` | `source`, `url`, `vintage` | Source attribution |

---

## Hooks

### useApiData<T>(endpoint)

Generic data fetching hook with TypeScript generics.

**Parameters**:
- `endpoint` — API endpoint path (e.g., `/indicators.json`)

**Returns**:
- `data: T | null` — Fetched data
- `loading: boolean` — Loading state
- `error: string | null` — Error message

**Behavior**:
1. Tries static JSON file first (`/data${endpoint}`)
2. Falls back to live API if static fails
3. Caches results in component state

### Specific Hooks

| Hook | Endpoint | Description |
|------|----------|-------------|
| `useAllIndicators()` | `/indicators.json` | All indicators |
| `useEconomicIndicators()` | `/economic.json` | Economic only |
| `useDemographicIndicators()` | `/demographics.json` | Demographic only |
| `useClimateIndicators()` | `/climate.json` | Climate only |
| `useDatasets()` | `/datasets.json` | Dataset catalog |
| `useMapLayers()` | `/map-layers.json` | Map layer definitions |
| `useNews()` | `/news.json` | News items |
| `useHealth()` | `/health.json` | Health check |
| `useStakeholderGroups()` | `/stakeholders.json` | Stakeholder groups |

---

## Pages

### HomePage (`/`)

Landing page with hero section, featured indicators, charts, and mission statement.

**Data Sources**:
- `useEconomicIndicators()` — Featured stats
- `useDemographicIndicators()` — Population stats
- `useClimateIndicators()` — Climate stats
- `useMapLayers()` — Map preview count
- `useDatasets()` — Dataset count

### DataExplorerPage (`/data`)

Searchable dataset catalog with filters and charts.

**Features**:
- Search by name/description
- Filter by category
- Filter by status
- Download CSV buttons
- Nivo charts for visualization

### MapsPage (`/`)

Interactive Leaflet map with toggleable layers.

**Features**:
- County boundary overlay
- City markers with population
- Layer category sidebar
- Quick toggles (boundary, cities)

### BusinessPage (`/business`)

Business dashboard with economic indicators and industry data.

**Featured Indicators**:
- Median household income
- Total establishments
- Total employment
- Average weekly wage

### ResidentsPage (`/residents`)

Resident-focused data including demographics and cost of living.

**Featured Indicators**:
- Population (2024)
- Median income
- Unemployment rate
- Cost of living index

### TouristsPage (`/tourist`)

Tourism data including hotel occupancy and visitor trends.

**Featured Indicators**:
- Hotel occupancy rate
- Average daily rate (ADR)
- RevPAR
- Monthly visitor volume

### LeadersPage (`/leaders`)

Investment and workforce data for decision-makers.

**Featured Indicators**:
- Capital investment by sector
- Workforce composition
- Permitting velocity
- Investment trends

---

## Routing

```tsx
<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="/data" element={<DataExplorerPage />} />
  <Route path="/maps" element={<MapsPage />} />
  <Route path="/business" element={<BusinessPage />} />
  <Route path="/residents" element={<ResidentsPage />} />
  <Route path="/tourists" element={<TouristsPage />} />
  <Route path="/leaders" element={<LeadersPage />} />
  <Route path="/news" element={<NewsPage />} />
  <Route path="*" element={<NotFoundPage />} />
</Routes>
```

---

## Styling

### Tailwind CSS

The project uses Tailwind CSS for utility-first styling.

**Custom Colors** (in `tailwind.config.js`):
```js
colors: {
  volusia: {
    navy: '#1a3a5c',
    blue: '#0d7377',
    teal: '#3d8b7d',
    gold: '#c9a84c',
    coral: '#e07a5f',
    slate: '#4a5568',
  }
}
```

### Nivo Charts

Nivo charts are configured with Volusia brand colors:

```tsx
colors={['#0d7377', '#c9a84c', '#3d8b7d', '#e07a5f', '#1a3a5c']}
```

### Leaflet Maps

OpenStreetMap tiles with custom styling.

---

## Build & Deploy

### Development

```bash
npm install
npm run dev          # http://localhost:5173
```

### Production Build

```bash
npm run build        # outputs to dist/
npm run preview      # http://localhost:4173
```

### Deployment

GitHub Actions automatically builds and deploys to GitHub Pages on push to `master`.

**Workflow** (`.github/workflows/deploy.yml`):
1. Checkout code
2. Setup Node.js
3. Install dependencies
4. Build project
5. Deploy `dist/` to `gh-pages` branch

---

## Testing

### Unit Tests

```bash
npm run test
```

### Type Checking

```bash
npm run lint         # tsc --noEmit
```

---

## Contributing

See [Contributing Guide](../contributing/guide.md) for general guidelines.

### Frontend-Specific Guidelines

1. Use functional components with hooks
2. TypeScript strict mode (no `any`)
3. Tailwind CSS for styling (no inline styles)
4. Responsive design (mobile-first)
5. Accessibility (ARIA labels, semantic HTML)

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
