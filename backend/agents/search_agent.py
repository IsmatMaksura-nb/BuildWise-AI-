

from datetime import datetime
from langsmith import traceable

from backend.tools.market_search import search_market_materials


class SearchAgent:

    def __init__(self):
        self.name = "BuildWise Search Agent"

    @traceable(
        name="BuildWise Market Search",
        run_type="chain"
    )
    def process(
        self,
        user_input: str,
        language: str = "English"
    ) -> str:
        """
        Search current construction market information.
        """

        is_bangla = language.lower() == "bangla"

        # -------------------------------------------------------------
        # Validate query
        # -------------------------------------------------------------

        if not user_input or not user_input.strip():

            if is_bangla:
                return (
                    "🔎 **সার্চ কুয়েরি পাওয়া যায়নি।**\n\n"
                    "আপনি কোন construction material বা market "
                    "information খুঁজছেন তা লিখুন।"
                )

            return (
                "🔎 **No search query provided.**\n\n"
                "Please enter the construction material or market "
                "information you want to search for."
            )

        # -------------------------------------------------------------
        # Market Search
        # -------------------------------------------------------------

        try:

            result = search_market_materials(
                query=user_input.strip()
            )

            # ---------------------------------------------------------
            # No result
            # ---------------------------------------------------------

            if not result.get("success", False):

                if is_bangla:
                    return (
                        "🔎 **নির্ভরযোগ্য মার্কেট প্রাইস পাওয়া যায়নি।**\n\n"
                        "দয়া করে material, brand বা product specification "
                        "আরও নির্দিষ্ট করে লিখুন।"
                    )

                return (
                    "🔎 **No reliable market price was found.**\n\n"
                    "Please provide a more specific material, brand, "
                    "or product specification."
                )

            # ---------------------------------------------------------
            # Get actual data returned by market_search.py
            # ---------------------------------------------------------

            results = result.get(
                "results",
                []
            )

            sources = result.get(
                "sources",
                []
            )

            material = result.get(
                "material",
                "construction material"
            )

            brand = result.get(
                "brand"
            )

            # Current search date
            search_date = datetime.now().strftime(
                "%d %B %Y"
            )

            # ---------------------------------------------------------
            # Best result
            # ---------------------------------------------------------

            best_result = (
                results[0]
                if results
                else None
            )

            # =========================================================
            # BANGLA REPORT
            # =========================================================

            if is_bangla:

                if best_result:

                    price = best_result.get(
                        "price"
                    )

                    price_high = best_result.get(
                        "price_high"
                    )

                    unit = best_result.get(
                        "unit",
                        ""
                    )

                    title = best_result.get(
                        "title",
                        "Requested product"
                    )

                    source = best_result.get(
                        "source",
                        "Web Search"
                    )

                    source_date = best_result.get(
                        "source_date"
                    )

                    # -------------------------------------------------
                    # Price formatting
                    # -------------------------------------------------

                    if price is not None:

                        if (
                            price_high is not None
                            and price_high != price
                        ):

                            price_text = (
                                f"৳{price:,.0f} - "
                                f"৳{price_high:,.0f}"
                            )

                        else:

                            price_text = (
                                f"৳{price:,.0f}"
                            )

                    else:

                        price_text = "মূল্য পাওয়া যায়নি"

                    # -------------------------------------------------
                    # Price-date status
                    # -------------------------------------------------

                    if source_date:

                        date_status = (
                            f"Source price date: {source_date}"
                        )

                    else:

                        date_status = (
                            "Source price date is not available. "
                            "The result was found during the current search."
                        )

                    # -------------------------------------------------
                    # Price Breakdown
                    # -------------------------------------------------

                    price_breakdown = (
                        f"**Product:** {title}\n\n"
                        f"**Price:** {price_text} / {unit}\n\n"
                        f"**Source:** {source}"
                    )

                    # -------------------------------------------------
                    # Market Notes
                    # -------------------------------------------------

                    market_notes = (
                        "⚠️ বাজারদর স্থান, বিক্রেতা, ব্র্যান্ড, "
                        "গ্রেড এবং সময় অনুযায়ী পরিবর্তিত হতে পারে।"
                    )

                    # -------------------------------------------------
                    # Multiple Sources
                    # -------------------------------------------------

                    source_list = (
                        "### 🔗 Sources\n\n"
                    )

                    if sources:

                        for i, src in enumerate(
                            sources[:3],
                            start=1
                        ):

                            src_name = src.get(
                                "source",
                                "Web Search"
                            )

                            src_url = src.get(
                                "url",
                                ""
                            )

                            if src_url:

                                source_list += (
                                    f"{i}. [{src_name}]"
                                    f"({src_url})\n"
                                )

                            else:

                                source_list += (
                                    f"{i}. {src_name}\n"
                                )

                    else:

                        source_list += (
                            f"1. {source}\n"
                        )

                    # -------------------------------------------------
                    # Summary
                    # -------------------------------------------------

                    summary = (
                        f"**{title}** এর সর্বশেষ পাওয়া "
                        f"দাম প্রায় **{price_text} / {unit}**।"
                    )

                else:

                    summary = (
                        "অনলাইনে নির্ভরযোগ্য বাজারমূল্য পাওয়া গেছে।"
                    )

                    date_status = (
                        "Source price date is not available."
                    )

                    price_breakdown = (
                        "নির্দিষ্ট price breakdown পাওয়া যায়নি।"
                    )

                    market_notes = ""

                    source_list = ""

                return (
                    "### 🔎 মার্কেট ইনফরমেশন\n\n"
                    f"{summary}\n\n"
                    f"**দামের তারিখ:** {date_status}\n\n"
                    "### 💰 Price Breakdown\n\n"
                    f"{price_breakdown}\n\n"
                    f"{market_notes}\n\n"
                    f"**Search Date:** {search_date}\n\n"
                    f"{source_list}"
                )

            # =========================================================
            # ENGLISH REPORT
            # =========================================================

            if best_result:

                price = best_result.get(
                    "price"
                )

                price_high = best_result.get(
                    "price_high"
                )

                unit = best_result.get(
                    "unit",
                    ""
                )

                title = best_result.get(
                    "title",
                    "Requested product"
                )

                source = best_result.get(
                    "source",
                    "Web Search"
                )

                source_date = best_result.get(
                    "source_date"
                )

                # -----------------------------------------------------
                # Price formatting
                # -----------------------------------------------------

                if price is not None:

                    if (
                        price_high is not None
                        and price_high != price
                    ):

                        price_text = (
                            f"৳{price:,.0f} - "
                            f"৳{price_high:,.0f}"
                        )

                    else:

                        price_text = (
                            f"৳{price:,.0f}"
                        )

                else:

                    price_text = "Price not available"

                # -----------------------------------------------------
                # Price-date status
                # -----------------------------------------------------

                if source_date:

                    date_status = (
                        f"Source price date: {source_date}"
                    )

                else:

                    date_status = (
                        "Source price date is not available. "
                        "The result was found during the current search."
                    )

                # -----------------------------------------------------
                # Price Breakdown
                # -----------------------------------------------------

                price_breakdown = (
                    f"**Product:** {title}\n\n"
                    f"**Price:** {price_text} / {unit}\n\n"
                    f"**Source:** {source}"
                )

                # -----------------------------------------------------
                # Market Notes
                # -----------------------------------------------------

                market_notes = (
                    "⚠️ Market prices may vary by location, "
                    "supplier, brand, grade, and time."
                )

                # -----------------------------------------------------
                # Multiple Sources
                # -----------------------------------------------------

                source_list = (
                    "### 🔗 Sources\n\n"
                )

                if sources:

                    for i, src in enumerate(
                        sources[:3],
                        start=1
                    ):

                        src_name = src.get(
                            "source",
                            "Web Search"
                        )

                        src_url = src.get(
                            "url",
                            ""
                        )

                        if src_url:

                            source_list += (
                                f"{i}. [{src_name}]"
                                f"({src_url})\n"
                            )

                        else:

                            source_list += (
                                f"{i}. {src_name}\n"
                            )

                else:

                    source_list += (
                        f"1. {source}\n"
                    )

                # -----------------------------------------------------
                # Summary
                # -----------------------------------------------------

                summary = (
                    f"**{title}** is currently reported at "
                    f"approximately **{price_text} per {unit}**."
                )

            else:

                summary = (
                    "A reliable market price was found."
                )

                date_status = (
                    "Source price date is not available."
                )

                price_breakdown = (
                    "No specific price breakdown was available."
                )

                market_notes = ""

                source_list = ""

            # ---------------------------------------------------------
            # Final English Response
            # ---------------------------------------------------------

            return (
                "### 🔎 Market Information\n\n"
                f"{summary}\n\n"
                f"**Price-date status:** {date_status}\n\n"
                "### 💰 Price Breakdown\n\n"
                f"{price_breakdown}\n\n"
                f"{market_notes}\n\n"
                f"**Search Date:** {search_date}\n\n"
                f"{source_list}"
            )

        # -------------------------------------------------------------
        # Error Handling
        # -------------------------------------------------------------

        except Exception as e:

            print(
                f"[SearchAgent] Error: {e}"
            )

            if is_bangla:

                return (
                    "❌ **মার্কেট সার্চে সমস্যা হয়েছে।**\n\n"
                    "দয়া করে আবার চেষ্টা করুন।"
                )

            return (
                "❌ **Market search failed.**\n\n"
                "Please try again."
            )


# =====================================================================
# FACTORY FUNCTION
# =====================================================================

def create_search_agent():
    """
    Create and return a SearchAgent instance.
    """

    return SearchAgent()