

from typing import Dict, Any, Optional

from langsmith import traceable

from backend.tools.cost_calculator import calculate_construction_cost


class CostAgent:

    def __init__(self):
        self.name = "BuildWise Cost Agent"

    # -----------------------------------------------------------------
    # LangSmith Trace
    # -----------------------------------------------------------------

    @traceable(
        name="BuildWise Cost Agent",
        process_inputs=lambda inputs: {
            "user_input": inputs.get("user_input"),
            "language": inputs.get("language"),
            "building_type": (inputs.get("extra_data") or {}).get("building_type"),
            "area_sqft": (inputs.get("extra_data") or {}).get("area_sqft"),
            "floors": (inputs.get("extra_data") or {}).get("floors"),
            "quality": (inputs.get("extra_data") or {}).get("quality"),
            "notes": (inputs.get("extra_data") or {}).get("notes"),
        },
        process_outputs=lambda output: {
            "status": "completed"
        }
    )
    def process(
        self,
        user_input: str,
        language: str = "English",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a planning-level construction cost estimate.

        The actual calculation is handled by cost_calculator.py.
        """

        is_bangla = language.lower() == "bangla"
        extra = extra_data or {}

        # -------------------------------------------------------------
        # Get construction information
        # -------------------------------------------------------------

        building_type = extra.get(
            "building_type",
            "Residential"
        )

        area_sqft = extra.get(
            "area_sqft",
            1500
        )

        floors = extra.get(
            "floors",
            1
        )

        quality = extra.get(
            "quality",
            "Standard"
        )

        notes = extra.get(
            "notes",
            user_input
        )

        # -------------------------------------------------------------
        # Validate numeric values
        # -------------------------------------------------------------

        try:
            area_sqft = float(area_sqft)
            floors = int(floors)

        except (TypeError, ValueError):

            if is_bangla:
                return (
                    "❌ **ভুল ইনপুট**\n\n"
                    "Area এবং floors-এর সঠিক numeric value দিন।"
                )

            return (
                "❌ **Invalid input**\n\n"
                "Please provide valid numeric values for "
                "area and number of floors."
            )

        if area_sqft <= 0 or floors <= 0:

            if is_bangla:
                return (
                    "❌ **ভুল ইনপুট**\n\n"
                    "Area এবং floors অবশ্যই 0-এর বেশি হতে হবে।"
                )

            return (
                "❌ **Invalid input**\n\n"
                "Area and number of floors must be greater than zero."
            )

        # -------------------------------------------------------------
        # Call existing cost calculation tool
        # -------------------------------------------------------------

        try:

            result = calculate_construction_cost(
                building_type=building_type,
                area_sqft=area_sqft,
                floors=floors,
                finish_quality=quality,
                notes=notes,
                is_bangla=is_bangla
            )

            return result["formatted_report"]

        except Exception as e:

            print(f"[CostAgent] Error: {e}")

            if is_bangla:
                return (
                    "❌ **Cost estimate তৈরি করতে সমস্যা হয়েছে।**\n\n"
                    "দয়া করে আবার চেষ্টা করুন।"
                )

            return (
                "❌ **Cost estimation failed.**\n\n"
                "Please check your inputs and try again."
            )


# =====================================================================
# FACTORY FUNCTION
# =====================================================================

def create_cost_agent():
    """
    Create and return a CostAgent instance.
    """
    return CostAgent()