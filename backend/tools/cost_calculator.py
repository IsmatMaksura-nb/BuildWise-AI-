
from typing import Dict, Any

BASE_RATES = {
    "residential": {
        "economy": 2000,
        "standard": 2500,
        "medium": 3000,
        "premium": 3800,
        "luxury": 4500
    },

    "commercial": {
        "economy": 2600,
        "standard": 3200,
        "medium": 3800,
        "premium": 4800,
        "luxury": 6000
    },

    "industrial": {
        "economy": 1600,
        "standard": 2000,
        "medium": 2400,
        "premium": 3000,
        "luxury": 3600
    },

    "duplex": {
        "economy": 2600,
        "standard": 3200,
        "medium": 3800,
        "premium": 4800,
        "luxury": 6000
    },

    "semi-pucca": {
        "economy": 1200,
        "standard": 1500,
        "medium": 1800,
        "premium": 2200,
        "luxury": 2700
    }
}


# =====================================================================
# 2. COST BREAKDOWN
# =====================================================================
# Total construction cost distribution.
#
# The percentages add up to 100%.

PERCENTAGE_BREAKDOWN = {
    "foundation_and_structure": 0.46,
    "masonry_and_plaster": 0.18,
    "plumbing_sanitary": 0.07,
    "electrical_fixtures": 0.05,
    "tiles_finishing_paint": 0.10,
    "labor_and_supervision": 0.14
}


# =====================================================================
# 3. CONTINGENCY
# =====================================================================
# Optional allowance for unexpected changes and minor cost variation.

DEFAULT_CONTINGENCY_RATE = 0.10


# =====================================================================
# 4. LABELS
# =====================================================================

BREAKDOWN_LABELS_EN = {
    "foundation_and_structure":
        "Foundation & Structural Works",
    "masonry_and_plaster":
        "Brick Masonry & Plaster Works",
    "plumbing_sanitary":
        "Plumbing, Drainage & Sanitary",
    "electrical_fixtures":
        "Electrical Wiring & Fixtures",
    "tiles_finishing_paint":
        "Tiles, Painting & Finishing",
    "labor_and_supervision":
        "Labor & Site Supervision"
}


BREAKDOWN_LABELS_BN = {
    "foundation_and_structure":
        "ফাউন্ডেশন ও স্ট্রাকচারাল কাজ",
    "masonry_and_plaster":
        "ইটের গাঁথুনি ও প্লাস্টার",
    "plumbing_sanitary":
        "প্লাম্বিং, ড্রেনেজ ও স্যানিটারি",
    "electrical_fixtures":
        "ইলেকট্রিক্যাল ওয়্যারিং ও ফিক্সচার",
    "tiles_finishing_paint":
        "টাইলস, পেইন্টিং ও ফিনিশিং",
    "labor_and_supervision":
        "শ্রমিক ও সাইট সুপারভিশন"
}


# =====================================================================
# 5. HELPER FUNCTIONS
# =====================================================================

def _format_number(value: float) -> str:
    """Formats a number using standard comma separators."""
    return f"{value:,.0f}"


def _normalize_building_type(building_type: str) -> str:
    """Normalizes building type and falls back to residential."""
    if not building_type:
        return "residential"

    key = str(building_type).lower().strip()

    aliases = {
        "residential building": "residential",
        "house": "residential",
        "home": "residential",

        "commercial building": "commercial",
        "office": "commercial",
        "shop": "commercial",

        "factory": "industrial",
        "factory building": "industrial",

        "duplex house": "duplex",
        "duplex home": "duplex",

        "semi pucca": "semi-pucca",
        "semi_pucca": "semi-pucca"
    }

    key = aliases.get(key, key)

    if key not in BASE_RATES:
        key = "residential"

    return key


def _normalize_quality(
    finish_quality: str,
    building_type: str
) -> str:
    """Normalizes finish quality and falls back to standard."""
    if not finish_quality:
        return "standard"

    key = str(finish_quality).lower().strip()

    aliases = {
        "basic": "economy",
        "low": "economy",
        "economic": "economy",

        "mid": "medium",
        "mid-range": "medium",
        "mid range": "medium",

        "high": "premium",
        "high-end": "premium",
        "high end": "premium"
    }

    key = aliases.get(key, key)

    if key not in BASE_RATES[building_type]:
        key = "standard"

    return key


# =====================================================================
# 6. MAIN COST CALCULATOR
# =====================================================================

def calculate_construction_cost(
    building_type: str = "Residential",
    area_sqft: float = 1500,
    floors: int = 1,
    finish_quality: str = "Standard",
    notes: str = "",
    is_bangla: bool = False
) -> Dict[str, Any]:
    """
    Calculates a planning-level construction cost estimate.

    Parameters
    ----------
    building_type : str
        Residential, Commercial, Industrial, Duplex, or Semi-Pucca.

    area_sqft : float
        Approximate floor area in square feet for ONE floor.

    floors : int
        Number of floors.

    finish_quality : str
        Economy, Standard, Medium, Premium, or Luxury.

    notes : str
        Additional project specifications.

    is_bangla : bool
        Whether the formatted report should be in Bangla.

    Returns
    -------
    Dict[str, Any]
        Cost calculation data and formatted report.
    """

    # =================================================================
    # 6.1 INPUT VALIDATION
    # =================================================================

    try:
        area_sqft = float(area_sqft)
    except (TypeError, ValueError):
        raise ValueError(
            "Area must be a valid positive number."
        )

    try:
        floors = int(floors)
    except (TypeError, ValueError):
        raise ValueError(
            "Number of floors must be a valid positive integer."
        )

    if area_sqft <= 0:
        raise ValueError(
            "Area must be greater than 0 square feet."
        )

    if floors <= 0:
        raise ValueError(
            "Number of floors must be at least 1."
        )

    # Prevent unrealistic accidental input.
    if area_sqft > 1_000_000:
        raise ValueError(
            "Area is too large. Please provide a realistic project area."
        )

    if floors > 100:
        raise ValueError(
            "Number of floors is too large for this planning estimator."
        )

    # =================================================================
    # 6.2 NORMALIZE INPUTS
    # =================================================================

    b_type_key = _normalize_building_type(building_type)

    q_key = _normalize_quality(
        finish_quality,
        b_type_key
    )

    # =================================================================
    # 6.3 GET BASE RATE
    # =================================================================

    base_rate_per_sqft = BASE_RATES[b_type_key][q_key]

    # =================================================================
    # 6.4 MULTI-FLOOR ADJUSTMENT
    # =================================================================
    # Higher buildings can require additional structural/foundation
    # allowance at planning level.

    floor_adjustment = 1.0

    if floors >= 10:
        floor_adjustment = 1.15
    elif floors >= 7:
        floor_adjustment = 1.12
    elif floors >= 4:
        floor_adjustment = 1.08

    adjusted_rate = base_rate_per_sqft * floor_adjustment

    # =================================================================
    # 6.5 TOTAL BUILT-UP AREA
    # =================================================================

    total_area = area_sqft * floors

    # =================================================================
    # 6.6 BASE CONSTRUCTION COST
    # =================================================================

    base_construction_cost = (
        total_area * adjusted_rate
    )

    # =================================================================
    # 6.7 ITEMIZED BREAKDOWN
    # =================================================================

    breakdown = {}

    for item, percentage in PERCENTAGE_BREAKDOWN.items():
        breakdown[item] = round(
            base_construction_cost * percentage
        )

    # =================================================================
    # 6.8 CONTINGENCY
    # =================================================================

    contingency = round(
        base_construction_cost *
        DEFAULT_CONTINGENCY_RATE
    )

    estimated_total = round(
        base_construction_cost + contingency
    )

    # =================================================================
    # 6.9 DISPLAY LABEL
    # =================================================================

    if b_type_key == "residential":
        display_building_type = "Residential"
    elif b_type_key == "commercial":
        display_building_type = "Commercial"
    elif b_type_key == "industrial":
        display_building_type = "Industrial"
    elif b_type_key == "duplex":
        display_building_type = "Duplex"
    else:
        display_building_type = "Semi-Pucca"

    quality_display = q_key.capitalize()

    # =================================================================
    # 6.10 ENGLISH REPORT
    # =================================================================

    if not is_bangla:

        report_lines = [
            "💰 **Planning-Level Construction Cost Estimate**",
            "",
            "📋 **Project Parameters:**",
            f"- **Building Type:** {display_building_type}",
            f"- **Area per Floor:** {_format_number(area_sqft)} sq.ft.",
            f"- **Number of Floors:** {floors}",
            f"- **Total Built-up Area:** {_format_number(total_area)} sq.ft.",
            f"- **Finish Quality:** {quality_display}",
        ]

        if notes:
            report_lines.append(
                f"- **Additional Specifications:** {notes}"
            )

        report_lines.extend([
            "",
            "📊 **Estimated Cost Breakdown:**"
        ])

        for item, amount in breakdown.items():
            label = BREAKDOWN_LABELS_EN[item]
            percentage = int(
                PERCENTAGE_BREAKDOWN[item] * 100
            )

            report_lines.append(
                f"- **{label}:** "
                f"৳ {_format_number(amount)} "
                f"({percentage}%)"
            )

        report_lines.extend([
            "",
            "────────────────────────────────────",
            f"🏗️ **Base Construction Cost:** "
            f"৳ {_format_number(base_construction_cost)}",
            f"🛡️ **Contingency Allowance (10%):** "
            f"৳ {_format_number(contingency)}",
            "",
            f"🏆 **Estimated Total Budget:** "
            f"৳ {_format_number(estimated_total)}",
            f"📌 **Estimated Rate:** "
            f"৳ {_format_number(adjusted_rate)} / sq.ft.",
            "",
            "⚠️ **Important:** This is a planning-level estimate, "
            "not a professional BOQ. Actual cost may vary depending "
            "on soil condition, foundation type, structural design, "
            "location, material brands, labor rates, approvals, "
            "utilities, and finishing specifications.",
            "",
            "💡 **For current material prices:** "
            "Use the BuildWise-AI Market Search feature."
        ])

        report = "\n".join(report_lines)

    # =================================================================
    # 6.11 BANGLA REPORT
    # =================================================================

    else:

        report_lines = [
            "💰 **নির্মাণ ব্যয়ের প্রাথমিক প্রাক্কলন**",
            "",
            "📋 **প্রকল্পের তথ্য:**",
            f"- **ভবনের ধরন:** {display_building_type}",
            f"- **প্রতি ফ্লোরের আয়তন:** "
            f"{_format_number(area_sqft)} বর্গফুট",
            f"- **ফ্লোর সংখ্যা:** {floors} তলা",
            f"- **মোট নির্মিত এলাকা:** "
            f"{_format_number(total_area)} বর্গফুট",
            f"- **ফিনিশিং মান:** {quality_display}",
        ]

        if notes:
            report_lines.append(
                f"- **অতিরিক্ত তথ্য:** {notes}"
            )

        report_lines.extend([
            "",
            "📊 **আনুমানিক খরচের বিভাজন:**"
        ])

        for item, amount in breakdown.items():
            label = BREAKDOWN_LABELS_BN[item]
            percentage = int(
                PERCENTAGE_BREAKDOWN[item] * 100
            )

            report_lines.append(
                f"- **{label}:** "
                f"৳ {_format_number(amount)} "
                f"({percentage}%)"
            )

        report_lines.extend([
            "",
            "────────────────────────────────────",
            f"🏗️ **মূল নির্মাণ ব্যয়:** "
            f"৳ {_format_number(base_construction_cost)}",
            f"🛡️ **Contingency (১০%):** "
            f"৳ {_format_number(contingency)}",
            "",
            f"🏆 **আনুমানিক মোট বাজেট:** "
            f"৳ {_format_number(estimated_total)}",
            f"📌 **আনুমানিক প্রতি বর্গফুট খরচ:** "
            f"৳ {_format_number(adjusted_rate)}",
            "",
            "⚠️ **গুরুত্বপূর্ণ:** এটি একটি প্রাথমিক "
            "পরিকল্পনামূলক হিসাব, পেশাদার BOQ নয়। মাটির অবস্থা, "
            "ফাউন্ডেশনের ধরন, structural design, অবস্থান, "
            "সামগ্রীর ব্র্যান্ড, শ্রমিকের মজুরি, অনুমোদন, "
            "ইউটিলিটি এবং ফিনিশিং অনুযায়ী প্রকৃত খরচ পরিবর্তিত "
            "হতে পারে।",
            "",
            "💡 **বর্তমান নির্মাণ সামগ্রীর বাজারদর জানতে:** "
            "BuildWise-AI-এর Market Search ব্যবহার করুন।"
        ])

        report = "\n".join(report_lines)

    # =================================================================
    # 6.12 RETURN RESULT
    # =================================================================

    return {
        "total_cost": estimated_total,
        "base_construction_cost": base_construction_cost,
        "contingency": contingency,
        "contingency_rate": DEFAULT_CONTINGENCY_RATE,
        "rate_per_sqft": adjusted_rate,
        "base_rate_per_sqft": base_rate_per_sqft,
        "total_area_sqft": total_area,
        "building_type": b_type_key,
        "finish_quality": q_key,
        "floors": floors,
        "area_per_floor_sqft": area_sqft,
        "floor_adjustment": floor_adjustment,
        "breakdown": breakdown,
        "formatted_report": report
    }