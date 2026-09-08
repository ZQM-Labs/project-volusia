# API Reference — Project Volusia

> Complete API endpoint reference for the Project Volusia backend.

---

## Base URL

| Environment | URL |
|-------------|-----|
| Local | `http://localhost:8790` |
| Cloudflare | `https://volusia.zqmlabs.com/api` |

---

## Endpoints

### Health & Status

#### `GET /api/health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "db_exists": true,
  "indicator_count": 26,
  "categories": ["Climate", "Demographics", "Economic", "Tourism"]
}
```

---

#### `GET /api/status`

Detailed system status.

**Response**:
```json
{
  "status": "operational",
  "indicators": 26,
  "categories": 4,
  "sources": 8,
  "sla": {
    "uptime": "99.9%",
    "response_time": "<200ms",
    "freshness": "95%"
  }
}
```

---

### Indicators

#### `GET /api/indicators`

List all indicators.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by category (Economic, Demographics, Climate, Tourism) |
| source | string | Filter by source |
| search | string | Search by name/description |

**Response**:
```json
{
  "count": 26,
  "indicators": [
    {
      "id": 1,
      "name": "total_population_pep_2024",
      "value": "601107",
      "unit": "persons",
      "category": "Demographics",
      "source": "US Census PEP",
      "source_url": "https://www2.census.gov/...",
      "vintage": "2024",
      "description": "Census PEP population estimate, July 1 2024"
    }
  ]
}
```

---

#### `GET /api/indicators/{name}`

Get a single indicator by name.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| name | string | Indicator name (URL-encoded) |

**Response**:
```json
{
  "id": 1,
  "name": "total_population_pep_2024",
  "value": "601107",
  "unit": "persons",
  "category": "Demographics",
  "source": "US Census PEP",
  "source_url": "https://www2.census.gov/...",
  "vintage": "2024",
  "description": "Census PEP population estimate, July 1 2024"
}
```

---

#### `GET /api/indicators.csv`

Download all indicators as CSV.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by category |

**Response**: CSV file download

---

### Datasets

#### `api/datasets`

Get dataset inventory.

**Response**:
```json
{
  "count": 26,
  "datasets": [
    {
      "id": 1,
      "source": "US Census PEP",
      "content": "",
      "fetched_at": "2026-09-07T12:00:00"
    }
  ]
}
```

---

### Map Layers

#### `GET /api/map-layers`

Get all map layers.

**Response**:
```json
{
  "count": 18,
  "layers": [
    {
      "id": 1,
      "name": "County Boundary",
      "category": "boundary",
      "description": "Volusia County outer boundary",
      "source": "US Census TIGER/Line",
      "format": "geojson"
    }
  ]
}
```

---

### Refresh

#### `POST /api/refresh`

Trigger a data refresh pipeline run.

**Response**:
```json
{
  "status": "triggered",
  "stdout_tail": "...",
  "returncode": 0
}
```

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad request |
| 404 | Resource not found |
| 500 | Internal server error |

**Error Response Format**:
```json
{
  "detail": "Error description"
}
```

---

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Authentication

Currently, the API is open and does not require authentication. Rate limiting is in place to prevent abuse.

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
