import json
import gzip
from typing import Dict, Any
from app.schemas.weather import WeatherDataResponse


class BandwidthOptimizationService:
    """
    Optimizes payload size for low-bandwidth, high-latency mobile networks.
    - Limits forecast arrays
    - Strips verbose climate baselines
    - Formats compact JSON key aliases
    - Compresses payloads with GZip
    """

    @staticmethod
    def optimize_weather_payload(weather: WeatherDataResponse) -> Dict[str, Any]:
        """Compresses weather model to minimal JSON dictionary for low-bandwidth mode."""
        raw = weather.model_dump()
        
        compact = {
            "loc": raw["location"]["name"],
            "lat": round(raw["location"]["latitude"], 2),
            "lon": round(raw["location"]["longitude"], 2),
            "curr": {
                "t": raw["current"]["temperature"],
                "fl": raw["current"]["apparent_temperature"],
                "h": raw["current"]["humidity"],
                "w": raw["current"]["wind_speed"],
                "cond": raw["current"]["condition_text"]
            },
            "fc": [
                {
                    "d": day["date"],
                    "min": day["temp_min"],
                    "max": day["temp_max"],
                    "pop": day["precipitation_probability"],
                    "cond": day["condition_text"]
                }
                for day in raw["daily_forecast"][:3]
            ],
            "alerts": [
                {
                    "ev": a["event"],
                    "sev": a["severity"],
                    "head": a["headline"],
                    "src": a["source"]
                }
                for a in raw.get("official_alerts", [])
            ],
            "lb": True
        }
        return compact

    @staticmethod
    def compress_bytes(json_data: dict) -> bytes:
        """GZip compresses dictionary into binary format for HTTP transfer."""
        raw_bytes = json.dumps(json_data).encode("utf-8")
        return gzip.compress(raw_bytes)


bandwidth_service = BandwidthOptimizationService()
