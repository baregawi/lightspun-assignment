# Data Directory

This directory contains structured JSON data files for the US States and Addresses API.

## Files Overview

### 1. `all_states.json`
Complete list of all 50 US states plus Washington DC (51 total).

**Structure:**
```json
{
  "states": [
    {"code": "AL", "name": "Alabama"},
    {"code": "AK", "name": "Alaska"},
    ...
  ],
  "total_count": 51
}
```

### 2. `state_municipalities.json`
Mapping of states to their municipalities, with focus on 3 sample states (CA, NY, TX) containing 20 municipalities each.

**Structure:**
```json
{
  "state_municipalities": {
    "CA": {
      "state_name": "California",
      "municipalities": [
        {"name": "Los Angeles", "type": "city"},
        {"name": "San Diego", "type": "city"},
        ...
      ]
    },
    ...
  },
  "sample_states": ["CA", "NY", "TX"],
  "total_sample_municipalities": 60
}
```

**Sample States & Municipalities:**
- **California (CA)**: 20 municipalities
  - Los Angeles, San Diego, San Jose, San Francisco, Fresno, Sacramento, Long Beach, Oakland, Bakersfield, Anaheim, Santa Ana, Riverside, Stockton, Irvine, Fremont, San Bernardino, Modesto, Fontana, Oxnard, Moreno Valley

- **New York (NY)**: 20 municipalities
  - New York City, Buffalo, Rochester, Yonkers, Syracuse, Albany, New Rochelle, Mount Vernon, Schenectady, Utica, White Plains, Hempstead, Troy, Niagara Falls, Binghamton, Freeport, Valley Stream, Long Beach, Rome, Jamestown

- **Texas (TX)**: 20 municipalities
  - Houston, San Antonio, Dallas, Austin, Fort Worth, El Paso, Arlington, Corpus Christi, Plano, Laredo, Lubbock, Garland, Irving, Amarillo, Grand Prairie, Brownsville, McKinney, Frisco, Pasadena, Killeen

### 3. `addresses_by_municipality_complete.json`
Complete address dataset with 100 sample addresses for each of the 60 municipalities.

**Structure:**
```json
{
  "addresses_by_municipality": {
    "CA": {
      "Los Angeles": [
        "123 Main St, Los Angeles, CA",
        "456 Oak Ave, Los Angeles, CA",
        ...
      ],
      ...
    },
    ...
  },
  "summary": {
    "total_states": 3,
    "municipalities_per_state": 20,
    "addresses_per_municipality": 100,
    "total_addresses": 6000
  }
}
```

### 4. `generate_addresses.py`
Python script used to generate the complete addresses dataset. Can be run to regenerate addresses with different random samples.

**Usage:**
```bash
cd data
python3 generate_addresses.py
```

## Data Statistics

| Metric | Value |
|--------|--------|
| **Total States** | 51 (50 states + DC) |
| **Sample States** | 3 (CA, NY, TX) |
| **Municipalities per Sample State** | 20 |
| **Total Sample Municipalities** | 60 |
| **Addresses per Municipality** | 100 |
| **Total Sample Addresses** | 6,000 |

## Address Format

All addresses follow the standard US format:
```
{house_number} {street_name} {street_type}, {municipality}, {state_code}
```

Examples:
- `1234 Main St, Los Angeles, CA`
- `5678 Oak Ave, Houston, TX`
- `9012 Park Blvd, New York City, NY`

## Usage

These files can be used to:

1. **Seed the database** - Import into PostgreSQL tables
2. **API testing** - Provide realistic test data
3. **Data analysis** - Geographic distribution studies
4. **Frontend development** - Populate dropdown menus and autocomplete

## Data Quality

- ✅ All addresses are unique within each municipality
- ✅ Street names use common American naming conventions
- ✅ House numbers range from 100-9999 for realism
- ✅ State codes are properly formatted (uppercase)
- ✅ Municipality names are real US cities/towns
- ✅ JSON structure is validated and properly formatted