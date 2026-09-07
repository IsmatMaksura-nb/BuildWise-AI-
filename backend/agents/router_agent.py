

from typing import Dict, Any


class RouterAgent:

    def __init__(self):
        self.name = "BuildWise Router Agent"

    def route(
        self,
        feature: str = "general",
        user_input: str = ""
    ) -> Dict[str, Any]:

        feature = (feature or "general").lower().strip()
        user_input = (user_input or "").lower().strip()

        # -------------------------------------------------------------
        # Direct feature mapping
        # -------------------------------------------------------------

        feature_map = {
            "doc": "document",
            "document": "document",

            "visual": "vision",
            "vision": "vision",

            "cost": "cost",

            "market": "search",
            "search": "search",

            "general": "general"
        }

        # If frontend already selected a feature,
        # use that feature directly.
        if feature in feature_map:

            selected_agent = feature_map[feature]

            return {
                "success": True,
                "agent": selected_agent,
                "reason": f"Feature '{feature}' selected.",
                "query": user_input
            }

        # -------------------------------------------------------------
        # Document keywords
        # -------------------------------------------------------------

        document_keywords = [
            "pdf",
            "document",
            "blueprint",
            "floor plan",
            "floorplan",
            "drawing",
            "specification",
            "spec",
            "room",
            "lift",
            "stair",
            "dimension",
            "building plan"
        ]

        # -------------------------------------------------------------
        # Vision keywords
        # -------------------------------------------------------------

        vision_keywords = [
            "image",
            "photo",
            "picture",
            "crack",
            "damp",
            "damage",
            "visual",
            "wall condition",
            "concrete condition"
        ]

        # -------------------------------------------------------------
        # Cost keywords
        # -------------------------------------------------------------

        cost_keywords = [
            "cost",
            "price estimate",
            "budget",
            "construction cost",
            "building cost",
            "estimate",
            "expense"
        ]

        # -------------------------------------------------------------
        # Search keywords
        # -------------------------------------------------------------

        search_keywords = [
            "market",
            "cement price",
            "rod price",
            "steel price",
            "brick price",
            "sand price",
            "tile price",
            "current price",
            "latest price"
        ]

        # -------------------------------------------------------------
        # Decide agent from user input
        # -------------------------------------------------------------

        if any(
            keyword in user_input
            for keyword in document_keywords
        ):
            return {
                "success": True,
                "agent": "document",
                "reason": "Document-related keywords detected.",
                "query": user_input
            }

        if any(
            keyword in user_input
            for keyword in vision_keywords
        ):
            return {
                "success": True,
                "agent": "vision",
                "reason": "Visual inspection keywords detected.",
                "query": user_input
            }

        if any(
            keyword in user_input
            for keyword in cost_keywords
        ):
            return {
                "success": True,
                "agent": "cost",
                "reason": "Cost-related keywords detected.",
                "query": user_input
            }

        if any(
            keyword in user_input
            for keyword in search_keywords
        ):
            return {
                "success": True,
                "agent": "search",
                "reason": "Market/search keywords detected.",
                "query": user_input
            }

        # -------------------------------------------------------------
        # General assistant
        # -------------------------------------------------------------

        return {
            "success": True,
            "agent": "general",
            "reason": "No specialized agent matched.",
            "query": user_input
        }


# =====================================================================
# GLOBAL ROUTER INSTANCE
# =====================================================================

router_agent = RouterAgent()