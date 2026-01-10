from typing import Any


class UnitConverterTool:
    """Unit conversion tool for various measurement types."""

    name = "unit_converter"
    description = "Convert between different units of measurement including length, weight, temperature, volume, area, speed, and data storage."

    # Conversion tables (to base unit)
    CONVERSIONS = {
        "length": {
            "base": "meter",
            "units": {
                "meter": 1,
                "m": 1,
                "kilometer": 1000,
                "km": 1000,
                "centimeter": 0.01,
                "cm": 0.01,
                "millimeter": 0.001,
                "mm": 0.001,
                "mile": 1609.344,
                "mi": 1609.344,
                "yard": 0.9144,
                "yd": 0.9144,
                "foot": 0.3048,
                "ft": 0.3048,
                "feet": 0.3048,
                "inch": 0.0254,
                "in": 0.0254,
                "nautical_mile": 1852,
            },
        },
        "weight": {
            "base": "kilogram",
            "units": {
                "kilogram": 1,
                "kg": 1,
                "gram": 0.001,
                "g": 0.001,
                "milligram": 0.000001,
                "mg": 0.000001,
                "metric_ton": 1000,
                "tonne": 1000,
                "pound": 0.453592,
                "lb": 0.453592,
                "lbs": 0.453592,
                "ounce": 0.0283495,
                "oz": 0.0283495,
                "stone": 6.35029,
            },
        },
        "volume": {
            "base": "liter",
            "units": {
                "liter": 1,
                "l": 1,
                "milliliter": 0.001,
                "ml": 0.001,
                "gallon": 3.78541,
                "gal": 3.78541,
                "quart": 0.946353,
                "qt": 0.946353,
                "pint": 0.473176,
                "pt": 0.473176,
                "cup": 0.236588,
                "fluid_ounce": 0.0295735,
                "fl_oz": 0.0295735,
                "tablespoon": 0.0147868,
                "tbsp": 0.0147868,
                "teaspoon": 0.00492892,
                "tsp": 0.00492892,
                "cubic_meter": 1000,
                "m3": 1000,
            },
        },
        "area": {
            "base": "square_meter",
            "units": {
                "square_meter": 1,
                "m2": 1,
                "sq_m": 1,
                "square_kilometer": 1000000,
                "km2": 1000000,
                "square_centimeter": 0.0001,
                "cm2": 0.0001,
                "hectare": 10000,
                "ha": 10000,
                "acre": 4046.86,
                "square_mile": 2589988.11,
                "sq_mi": 2589988.11,
                "square_foot": 0.092903,
                "sq_ft": 0.092903,
                "square_yard": 0.836127,
                "sq_yd": 0.836127,
            },
        },
        "speed": {
            "base": "meter_per_second",
            "units": {
                "meter_per_second": 1,
                "m/s": 1,
                "mps": 1,
                "kilometer_per_hour": 0.277778,
                "km/h": 0.277778,
                "kph": 0.277778,
                "kmh": 0.277778,
                "mile_per_hour": 0.44704,
                "mph": 0.44704,
                "knot": 0.514444,
                "kt": 0.514444,
                "foot_per_second": 0.3048,
                "ft/s": 0.3048,
            },
        },
        "data": {
            "base": "byte",
            "units": {
                "bit": 0.125,
                "byte": 1,
                "b": 1,
                "kilobyte": 1024,
                "kb": 1024,
                "megabyte": 1048576,
                "mb": 1048576,
                "gigabyte": 1073741824,
                "gb": 1073741824,
                "terabyte": 1099511627776,
                "tb": 1099511627776,
                "petabyte": 1125899906842624,
                "pb": 1125899906842624,
            },
        },
        "time": {
            "base": "second",
            "units": {
                "second": 1,
                "s": 1,
                "sec": 1,
                "millisecond": 0.001,
                "ms": 0.001,
                "microsecond": 0.000001,
                "minute": 60,
                "min": 60,
                "hour": 3600,
                "h": 3600,
                "hr": 3600,
                "day": 86400,
                "d": 86400,
                "week": 604800,
                "wk": 604800,
                "month": 2592000,  # 30 days
                "year": 31536000,  # 365 days
                "yr": 31536000,
            },
        },
    }

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
                        "value": {
                            "type": "number",
                            "description": "The numeric value to convert",
                        },
                        "from_unit": {
                            "type": "string",
                            "description": "The source unit (e.g., 'km', 'mile', 'kg', 'lb', 'celsius', 'fahrenheit')",
                        },
                        "to_unit": {
                            "type": "string",
                            "description": "The target unit to convert to",
                        },
                    },
                    "required": ["value", "from_unit", "to_unit"],
                },
            },
        }

    def _normalize_unit(self, unit: str) -> str:
        """Normalize unit names to handle plurals and variations."""
        unit = unit.lower().strip().replace(" ", "_")

        # Common plural/variation mappings
        aliases = {
            # Plurals
            "meters": "meter",
            "kilometers": "kilometer",
            "centimeters": "centimeter",
            "millimeters": "millimeter",
            "miles": "mile",
            "yards": "yard",
            "inches": "inch",
            "kilograms": "kilogram",
            "grams": "gram",
            "milligrams": "milligram",
            "pounds": "pound",
            "ounces": "ounce",
            "liters": "liter",
            "litres": "liter",
            "litre": "liter",
            "milliliters": "milliliter",
            "millilitres": "milliliter",
            "millilitre": "milliliter",
            "gallons": "gallon",
            "quarts": "quart",
            "pints": "pint",
            "cups": "cup",
            "fluid_ounces": "fluid_ounce",
            "floz": "fl_oz",
            "fl_ounce": "fluid_ounce",
            "fl_ounces": "fluid_ounce",
            "tablespoons": "tablespoon",
            "teaspoons": "teaspoon",
            "seconds": "second",
            "minutes": "minute",
            "hours": "hour",
            "days": "day",
            "weeks": "week",
            "months": "month",
            "years": "year",
            "bytes": "byte",
            "kilobytes": "kilobyte",
            "megabytes": "megabyte",
            "gigabytes": "gigabyte",
            "terabytes": "terabyte",
            # Common variations
            "kgs": "kg",
            "kms": "km",
            "hrs": "hour",
            "mins": "minute",
            "secs": "second",
        }

        return aliases.get(unit, unit)

    def _find_category(self, unit: str) -> tuple[str | None, str]:
        """Find which category a unit belongs to."""
        unit_normalized = self._normalize_unit(unit)
        for category, data in self.CONVERSIONS.items():
            if unit_normalized in data["units"]:
                return category, unit_normalized
        return None, unit_normalized

    def _convert_temperature(
        self, value: float, from_unit: str, to_unit: str
    ) -> dict[str, Any]:
        """Handle temperature conversions separately due to non-linear conversion."""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        # Normalize unit names
        temp_aliases = {
            "c": "celsius",
            "f": "fahrenheit",
            "k": "kelvin",
        }
        from_unit = temp_aliases.get(from_unit, from_unit)
        to_unit = temp_aliases.get(to_unit, to_unit)

        # Convert to Celsius first
        if from_unit == "celsius":
            celsius = value
        elif from_unit == "fahrenheit":
            celsius = (value - 32) * 5 / 9
        elif from_unit == "kelvin":
            celsius = value - 273.15
        else:
            return {
                "success": False,
                "error": f"Unknown temperature unit: {from_unit}",
            }

        # Convert from Celsius to target
        if to_unit == "celsius":
            result = celsius
        elif to_unit == "fahrenheit":
            result = celsius * 9 / 5 + 32
        elif to_unit == "kelvin":
            result = celsius + 273.15
        else:
            return {
                "success": False,
                "error": f"Unknown temperature unit: {to_unit}",
            }

        return {
            "success": True,
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "result": round(result, 4),
            "category": "temperature",
        }

    def execute(
        self, value: float, from_unit: str, to_unit: str
    ) -> dict[str, Any]:
        """
        Convert a value from one unit to another.

        Args:
            value: The numeric value to convert
            from_unit: The source unit
            to_unit: The target unit

        Returns:
            Dictionary containing the conversion result
        """
        try:
            from_unit_lower = from_unit.lower().strip()
            to_unit_lower = to_unit.lower().strip()

            # Check for temperature (special case)
            temp_units = {"celsius", "fahrenheit", "kelvin", "c", "f", "k"}
            if from_unit_lower in temp_units or to_unit_lower in temp_units:
                return self._convert_temperature(value, from_unit, to_unit)

            # Find categories for both units
            from_category, from_normalized = self._find_category(from_unit)
            to_category, to_normalized = self._find_category(to_unit)

            if not from_category:
                return {
                    "success": False,
                    "error": f"Unknown unit: {from_unit}",
                    "supported_categories": list(self.CONVERSIONS.keys())
                    + ["temperature"],
                }

            if not to_category:
                return {
                    "success": False,
                    "error": f"Unknown unit: {to_unit}",
                    "supported_categories": list(self.CONVERSIONS.keys())
                    + ["temperature"],
                }

            if from_category != to_category:
                return {
                    "success": False,
                    "error": f"Cannot convert between different categories: {from_category} and {to_category}",
                }

            # Get conversion factors
            category_data = self.CONVERSIONS[from_category]
            from_factor = category_data["units"][from_normalized]
            to_factor = category_data["units"][to_normalized]

            # Convert: value * from_factor gives base unit, / to_factor gives target
            result = value * from_factor / to_factor

            # Round appropriately
            if abs(result) >= 1:
                result = round(result, 6)
            else:
                result = round(result, 10)

            return {
                "success": True,
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": result,
                "category": from_category,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Conversion error: {str(e)}",
            }
