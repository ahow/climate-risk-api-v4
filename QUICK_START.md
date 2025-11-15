# Climate Risk API V4 - Quick Start Guide

Get started with the Climate Risk API in 5 minutes.

---

## API URLs

**Original API (Coordinates & Countries):**  
`https://climate-risk-api-v4-7da6992dc867.herokuapp.com/`

**Country API (Coordinates & Countries):**  
`https://climate-risk-country-v4-fdee3b254d49.herokuapp.com/`

**Note:** Both APIs support both endpoints. Use either one.

---

## 1. Test the API

### Health Check
```bash
curl https://climate-risk-api-v4-7da6992dc867.herokuapp.com/health
```

**Expected Response:**
```json
{
    "status": "healthy",
    "hadex3_loaded": 7,
    "flood_lookup_points": 7473,
    "hurricane_data": true
}
```

---

## 2. Assess Climate Risk by Coordinates

### Example: Miami, Florida

```bash
curl -X POST https://climate-risk-api-v4-7da6992dc867.herokuapp.com/assess \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 25.76,
    "longitude": -80.19,
    "asset_value": 1000000
  }'
```

### Key Results:
- **Expected Annual Loss:** $5,941 (0.59% of asset value)
- **30-Year Present Value:** $67,889 (6.79% of asset value)
- **Primary Risks:** Drought (0.42%), Hurricane (0.17%)
- **Response Time:** ~12 seconds

---

## 3. Assess Climate Risk by Country

### Example: Bangladesh

```bash
curl -X POST https://climate-risk-country-v4-fdee3b254d49.herokuapp.com/assess/country \
  -H "Content-Type: application/json" \
  -d '{
    "country": "Bangladesh",
    "asset_value": 1000000
  }'
```

### Key Results:
- **Expected Annual Loss:** $13,680 (1.37% of asset value)
- **30-Year Present Value:** $156,313 (15.63% of asset value)
- **Primary Risks:** Extreme Precipitation (1.04%), Drought (0.17%), Heat (0.16%)
- **Assessment Location:** Population-weighted center of Bangladesh
- **Response Time:** ~12 seconds

---

## 4. Supported Countries (50 Total)

**Americas:** United States, Brazil, Mexico, Colombia, Argentina, Peru, Venezuela, Canada

**Asia:** China, India, Indonesia, Pakistan, Bangladesh, Japan, Philippines, Vietnam, Thailand, Myanmar, South Korea, Nepal, Malaysia, Uzbekistan, Iraq, Iran, Saudi Arabia, Yemen, Turkey

**Europe:** Russia, Germany, United Kingdom, France, Italy, Spain, Poland, Ukraine

**Africa:** Nigeria, Ethiopia, Egypt, South Africa, Tanzania, Kenya, Uganda, Sudan, Algeria, Morocco, Angola, Mozambique, Ghana, Madagascar

**Oceania:** Australia

---

## 5. Understanding the Results

### Expected Annual Loss (EAL)
The average annual financial loss due to climate risks, calculated as:

**EAL = Probability × Severity × Asset Value**

**Example:** Miami with $1M asset value has EAL of $5,941 (0.59%)

### 30-Year Present Value
Total expected losses over 30 years, discounted to present value:
- **Discount Rate:** 10% (standard financial rate)
- **Climate Escalation:** 2% annual increase in risk
- **Time Horizon:** 30 years

**Example:** Miami's 30-year present value is $67,889 (6.79%)

### Risk Breakdown
Individual risk contributions:
- **Hurricane:** Based on NOAA historical storm data (1974-2024)
- **Flood:** Based on WRI 100-year flood maps
- **Drought:** Based on HadEX3 consecutive dry days (1901-2018)
- **Heat Stress:** Based on HadEX3 maximum temperatures
- **Extreme Precipitation:** Based on HadEX3 5-day rainfall maxima

---

## 6. Python Integration

```python
import requests

def assess_climate_risk(latitude, longitude, asset_value=1000000):
    """Assess climate risk for a specific location"""
    url = "https://climate-risk-api-v4-7da6992dc867.herokuapp.com/assess"
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "asset_value": asset_value
    }
    response = requests.post(url, json=payload)
    return response.json()

def assess_country_risk(country, asset_value=1000000):
    """Assess climate risk for a country"""
    url = "https://climate-risk-country-v4-fdee3b254d49.herokuapp.com/assess/country"
    payload = {
        "country": country,
        "asset_value": asset_value
    }
    response = requests.post(url, json=payload)
    return response.json()

# Example usage
miami_risk = assess_climate_risk(25.76, -80.19, 1000000)
print(f"Miami Annual Loss: ${miami_risk['expected_annual_loss']:,.2f}")

bangladesh_risk = assess_country_risk("Bangladesh", 1000000)
print(f"Bangladesh Annual Loss: ${bangladesh_risk['expected_annual_loss']:,.2f}")
```

---

## 7. Common Use Cases

### Real Estate Due Diligence
Assess climate risk for property acquisitions:
```python
property_value = 5000000
location = (40.7128, -74.0060)  # New York City
risk = assess_climate_risk(*location, property_value)
print(f"Annual Climate Risk: ${risk['expected_annual_loss']:,.2f}")
```

### Portfolio Analysis
Analyze climate exposure across multiple assets:
```python
portfolio = [
    {"name": "Miami Office", "lat": 25.76, "lon": -80.19, "value": 10000000},
    {"name": "Houston Warehouse", "lat": 29.76, "lon": -95.37, "value": 5000000},
    {"name": "NYC Retail", "lat": 40.71, "lon": -74.01, "value": 15000000}
]

total_risk = 0
for asset in portfolio:
    risk = assess_climate_risk(asset["lat"], asset["lon"], asset["value"])
    print(f"{asset['name']}: ${risk['expected_annual_loss']:,.2f}")
    total_risk += risk['expected_annual_loss']

print(f"\nTotal Portfolio Risk: ${total_risk:,.2f}")
```

### Country-Level Screening
Screen countries for climate risk exposure:
```python
countries = ["United States", "Bangladesh", "Philippines", "Japan"]

for country in countries:
    risk = assess_country_risk(country, 1000000)
    print(f"{country}: {risk['expected_annual_loss_pct']:.2%}")
```

---

## 8. Response Time Expectations

| Scenario | Response Time |
|----------|---------------|
| First request (cold start) | 8-12 seconds |
| Subsequent requests | 11-13 seconds |
| Heroku timeout limit | 30 seconds (hard limit) |

**Note:** All requests complete well within the 30-second timeout.

---

## 9. Error Handling

```python
import requests

def safe_assess_risk(latitude, longitude, asset_value=1000000):
    """Assess risk with error handling"""
    try:
        url = "https://climate-risk-api-v4-7da6992dc867.herokuapp.com/assess"
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "asset_value": asset_value
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timeout (>60s)"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

# Usage
result = safe_assess_risk(25.76, -80.19)
if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Risk: {result['expected_annual_loss_pct']:.2%}")
```

---

## 10. Next Steps

### Full Documentation
See `DEPLOYMENT_GUIDE.md` for:
- Complete API reference
- Data source details
- Risk calibration methodology
- Deployment architecture
- Maintenance procedures

### GitHub Repository
**URL:** https://github.com/ahow/climate-risk-api-v4

**Features:**
- Complete source code
- Climate data files
- Deployment configuration
- Issue tracking

### Support
- **Report Issues:** GitHub Issues
- **Request Features:** GitHub Issues
- **Contribute:** Pull requests welcome

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ CLIMATE RISK API V4 - QUICK REFERENCE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ BASE URL (Either one):                                      │
│   https://climate-risk-api-v4-7da6992dc867.herokuapp.com/   │
│   https://climate-risk-country-v4-fdee3b254d49.herokuapp.com│
│                                                              │
│ ENDPOINTS:                                                   │
│   GET  /health                - Health check                │
│   POST /assess                - Coordinate assessment       │
│   POST /assess/country        - Country assessment          │
│                                                              │
│ COORDINATE ASSESSMENT:                                       │
│   {                                                          │
│     "latitude": 25.76,                                       │
│     "longitude": -80.19,                                     │
│     "asset_value": 1000000                                   │
│   }                                                          │
│                                                              │
│ COUNTRY ASSESSMENT:                                          │
│   {                                                          │
│     "country": "Bangladesh",                                 │
│     "asset_value": 1000000                                   │
│   }                                                          │
│                                                              │
│ RESPONSE TIME: 11-13 seconds                                │
│ TIMEOUT LIMIT: 30 seconds                                   │
│ SUPPORTED COUNTRIES: 50                                      │
│ DATA SOURCES: NOAA, WRI, HadEX3                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Ready to start?** Copy any example above and run it now!

For detailed documentation, see `DEPLOYMENT_GUIDE.md`.

