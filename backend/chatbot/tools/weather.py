import urllib.request
import urllib.parse
import json
from typing import Any
from chatbot.config import settings


class WeatherTool:
    """Weather information tool using OpenWeatherMap API."""

    name = "weather"
    description = "Get current weather information for any city or location. Returns temperature, conditions, humidity, and wind speed."

    def get_schema(self) -> dict:
        """Return OpenAI-compatible function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, optionally with country code (e.g., 'London', 'New York, US', 'Tokyo, JP')",
                        },
                        "units": {
                            "type": "string",
                            "enum": ["metric", "imperial"],
                            "description": "Temperature units: 'metric' for Celsius, 'imperial' for Fahrenheit (default: metric)",
                        },
                    },
                    "required": ["location"],
                },
            },
        }

    def execute(self, location: str, units: str = "metric") -> dict[str, Any]:
        """
        Get current weather for a location.

        Args:
            location: City name (optionally with country code)
            units: Temperature units ('metric' or 'imperial')

        Returns:
            Dictionary containing weather information
        """
        try:
            api_key = getattr(settings, "OPENWEATHERMAP_API_KEY", "")
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenWeatherMap API key not configured",
                    "location": location,
                }

            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": units,
            }

            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            # Extract relevant weather information
            temp_unit = "°C" if units == "metric" else "°F"
            speed_unit = "m/s" if units == "metric" else "mph"

            weather = data.get("weather", [{}])[0]
            main = data.get("main", {})
            wind = data.get("wind", {})
            sys = data.get("sys", {})

            return {
                "success": True,
                "location": data.get("name", location),
                "country": sys.get("country", ""),
                "temperature": f"{main.get('temp', 'N/A')}{temp_unit}",
                "feels_like": f"{main.get('feels_like', 'N/A')}{temp_unit}",
                "temp_min": f"{main.get('temp_min', 'N/A')}{temp_unit}",
                "temp_max": f"{main.get('temp_max', 'N/A')}{temp_unit}",
                "humidity": f"{main.get('humidity', 'N/A')}%",
                "condition": weather.get("main", "Unknown"),
                "description": weather.get("description", ""),
                "wind_speed": f"{wind.get('speed', 'N/A')} {speed_unit}",
                "pressure": f"{main.get('pressure', 'N/A')} hPa",
            }

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {
                    "success": False,
                    "error": f"Location '{location}' not found. Try using format: 'City, Country Code'",
                    "location": location,
                }
            return {
                "success": False,
                "error": f"API error: {e.code}",
                "location": location,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "location": location,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Weather fetch error: {str(e)}",
                "location": location,
            }
