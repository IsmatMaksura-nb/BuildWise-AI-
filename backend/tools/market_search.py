

import re
from datetime import datetime
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional

from tavily import TavilyClient


# =====================================================================
# 1. CONFIGURATION
# =====================================================================

try:
    from backend.config import settings
    TAVILY_API_KEY = settings.TAVILY_API_KEY
except Exception:
    TAVILY_API_KEY = None

CURRENT_YEAR = datetime.now().year


# =====================================================================
# 2. BLOCKED / LOW-QUALITY DOMAINS
# =====================================================================

BAD_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "pinterest.com",
    "x.com",
    "twitter.com",

    "investing.com",
    "stockanalysis.com",
    "marketscreener.com",
    "tradingview.com",
    "marketwatch.com",
}

SOCIAL_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "pinterest.com",
    "x.com",
    "twitter.com",
}

FINANCIAL_DOMAINS = {
    "investing.com",
    "stockanalysis.com",
    "marketscreener.com",
    "tradingview.com",
    "marketwatch.com",
}


# =====================================================================
# 3. CEMENT BRANDS
# =====================================================================

CEMENT_BRANDS = {
    "bashundhara": ["bashundhara"],
    "shah": ["shah"],
    "crown": ["crown"],
    "fresh": ["fresh"],
    "akij": ["akij"],
    "premier": ["premier"],
    "seven rings": ["seven rings", "sevenrings"],
    "scan": ["scan"],
    "holcim": ["holcim"],
    "lafarge": ["lafarge"],
    "confidence": ["confidence"],
    "mir": ["mir"],
    "supercrete": ["supercrete"],
    "king": ["king"],
    "ruby": ["ruby"],
    "diamond": ["diamond"],
    "metrocem": ["metrocem"],
    "meghna": ["meghna"],
    "unique": ["unique"],
}


# =====================================================================
# 4. ROD / STEEL BRANDS
# =====================================================================

ROD_BRANDS = {
    "bsrm": ["bsrm"],
    "ksrm": ["ksrm"],
    "gph": ["gph"],
    "aks": ["aks"],
    "anwar": ["anwar"],
    "rahim": ["rahim"],
    "kabir": ["kabir"],
    "bms": ["bms"],
    "rani": ["rani"],
}


# =====================================================================
# 5. NORMALIZATION
# =====================================================================

def _normalize(text: Any) -> str:

    if text is None:
        return ""

    text = str(text).lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("৳", " taka ")
    text = text.replace("tk.", " tk ")
    text = text.replace("taka", " taka ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================================
# 6. URL / DOMAIN HELPERS
# =====================================================================

def _domain(url: str) -> str:

    try:
        host = urlparse(url).netloc.lower()

        if host.startswith("www."):
            host = host[4:]

        return host

    except Exception:
        return ""


def _source_name(url: str) -> str:

    domain = _domain(url)

    source_map = {
        "bdstall.com": "BDStall",
        "tbsnews.net": "The Business Standard",
        "thedailystar.net": "The Daily Star",
        "cemnet.com": "CemNet",
        "dhaka-mokam.com": "Dhaka Mokam",
        "banglastall.com": "BanglaStall",
        "tigercementbd.com": "Tiger Cement",
        "mircement.com": "Mir Cement",
        "bddigest.com": "BD Digest",
        "farmacsteel.com": "Farmac Steel",
        "bsrm.com": "BSRM",
        "ksrm.com.bd": "KSRM",
    }

    for key, value in source_map.items():

        if domain == key or domain.endswith("." + key):
            return value

    return domain or "Web"


def _is_bad_domain(url: str) -> bool:

    domain = _domain(url)

    for bad in BAD_DOMAINS:

        if domain == bad or domain.endswith("." + bad):
            return True

    return False


def _is_social_domain(url: str) -> bool:

    domain = _domain(url)

    for bad in SOCIAL_DOMAINS:

        if domain == bad or domain.endswith("." + bad):
            return True

    return False


def _is_financial_domain(url: str) -> bool:

    domain = _domain(url)

    for bad in FINANCIAL_DOMAINS:

        if domain == bad or domain.endswith("." + bad):
            return True

    return False


# =====================================================================
# 7. MATERIAL DETECTION
# =====================================================================

def detect_material(query: str) -> str:

    q = _normalize(query)

    rod_keywords = [
        "rod",
        "steel rod",
        "rebar",
        "reinforcement",
        "tmt",
        "ms rod",
    ]

    cement_keywords = [
        "cement",
        "opc",
        "pcc",
        "portland",
    ]

    for word in rod_keywords:

        if word in q:
            return "rod"

    for word in cement_keywords:

        if word in q:
            return "cement"

    return "unknown"


# =====================================================================
# 8. BRAND DETECTION
# =====================================================================

def detect_brand(
    query: str,
    material: str
) -> Optional[str]:

    q = _normalize(query)

    if material == "rod":
        brand_map = ROD_BRANDS

    elif material == "cement":
        brand_map = CEMENT_BRANDS

    else:
        return None

    sorted_brands = sorted(
        brand_map.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for canonical, aliases in sorted_brands:

        for alias in aliases:

            alias_n = _normalize(alias)

            pattern = (
                rf"(?<![a-z0-9])"
                rf"{re.escape(alias_n)}"
                rf"(?![a-z0-9])"
            )

            if re.search(pattern, q):
                return canonical

    return None


# =====================================================================
# 9. GRADE DETECTION
# =====================================================================

def detect_grade(query: str) -> Optional[str]:

    q = _normalize(query)

    patterns = [

        # -------------------------------------------------------------
        # 500D / B500D / 500DWR / B500DWR
        # -------------------------------------------------------------

        (r"\bb500dwr\b", "500D"),
        (r"\b500dwr\b", "500D"),
        (r"\bb500 dwr\b", "500D"),
        (r"\b500 dwr\b", "500D"),

        (r"\bb500d\b", "500D"),
        (r"\b500d\b", "500D"),
        (r"\bb500 d\b", "500D"),
        (r"\b500 d\b", "500D"),

        # -------------------------------------------------------------
        # 500W / B500W
        # -------------------------------------------------------------

        (r"\bb500w\b", "500W"),
        (r"\b500w\b", "500W"),
        (r"\bb500 w\b", "500W"),
        (r"\b500 w\b", "500W"),

        # -------------------------------------------------------------
        # Grade 60
        # -------------------------------------------------------------

        (r"\b60 grade\b", "60 GRADE"),
        (r"\bgrade[- ]?60\b", "60 GRADE"),
        (r"\bgrade60\b", "60 GRADE"),
        (r"\b60g\b", "60 GRADE"),

        # -------------------------------------------------------------
        # Grade 75
        # -------------------------------------------------------------

        (r"\b75 grade\b", "75 GRADE"),
        (r"\bgrade[- ]?75\b", "75 GRADE"),
        (r"\bgrade75\b", "75 GRADE"),
        (r"\b75g\b", "75 GRADE"),

        # -------------------------------------------------------------
        # Cement
        # -------------------------------------------------------------

        (r"\bopc\b", "OPC"),
        (r"\bpcc\b", "PCC"),
    ]

    for pattern, normalized_grade in patterns:

        if re.search(pattern, q):
            return normalized_grade

    return None


# =====================================================================
# 10. GRADE MATCHING
# =====================================================================

def contains_grade(
    text: str,
    grade: Optional[str],
    brand: Optional[str] = None
) -> bool:

    if not grade:
        return False

    text_n = _normalize(text)
    brand_n = _normalize(brand) if brand else ""

    # -------------------------------------------------------------
    # 500D
    # -------------------------------------------------------------

    if grade.upper() == "500D":

        variations = [
            "500d",
            "500 d",
            "b500d",
            "b500 d",
            "500dwr",
            "500 dwr",
            "b500dwr",
            "b500 dwr",
            "b 500 d",
            "b 500 dwr",
        ]

        if any(
            _normalize(v) in text_n
            for v in variations
        ):
            return True

        # BSRM Xtreme DWR is treated as BSRM's
        # DWR product family only when BSRM is also present.
        #
        # Generic "DWR" alone is NOT enough.
        if brand_n == "bsrm":

            if re.search(
                r"\bbsrm\s+xtreme\s+dwr\b",
                text_n
            ):
                return True

            if (
                re.search(
                    r"\bxtreme\s+dwr\b",
                    text_n
                )
                and "bsrm" in text_n
            ):
                return True

        return False

    # -------------------------------------------------------------
    # 500W
    # -------------------------------------------------------------

    if grade.upper() == "500W":

        variations = [
            "500w",
            "500 w",
            "b500w",
            "b500 w",
            "b 500 w",
            "xtreme 500w",
            "xtreme-500w",
        ]

        return any(
            _normalize(v) in text_n
            for v in variations
        )

    # -------------------------------------------------------------
    # Grade 60
    # -------------------------------------------------------------

    if grade.upper() == "60 GRADE":

        variations = [
            "60 grade",
            "grade 60",
            "grade-60",
            "grade60",
            "60g",
        ]

        return any(
            _normalize(v) in text_n
            for v in variations
        )

    # -------------------------------------------------------------
    # Grade 75
    # -------------------------------------------------------------

    if grade.upper() == "75 GRADE":

        variations = [
            "75 grade",
            "grade 75",
            "grade-75",
            "grade75",
            "75g",
        ]

        return any(
            _normalize(v) in text_n
            for v in variations
        )

    # -------------------------------------------------------------
    # Cement
    # -------------------------------------------------------------

    if grade.upper() == "OPC":
        return "opc" in text_n

    if grade.upper() == "PCC":
        return "pcc" in text_n

    return _normalize(grade) in text_n


# =====================================================================
# 11. SEARCH QUERY BUILDER
# =====================================================================

def build_search_query(
    user_query: str,
    material: str,
    brand: Optional[str],
    grade: Optional[str],
) -> str:

    # -------------------------------------------------------------
    # CEMENT
    # -------------------------------------------------------------

    if material == "cement":

        if brand:

            return (
                f'"{brand}" cement '
                f'current price Bangladesh '
                f'{CURRENT_YEAR} '
                f'50kg bag'
            )

        return (
            f'current cement price Bangladesh '
            f'{CURRENT_YEAR} '
            f'50kg bag'
        )

    # -------------------------------------------------------------
    # ROD
    # -------------------------------------------------------------

    if material == "rod":

        if brand:

            search_query = (
                f'"{brand}" '
                f'"{brand} rod" '
                f'"{brand} steel" '
                f'"{brand} price" '
                f"current price Bangladesh "
                f"{CURRENT_YEAR} "
            )

            if grade == "500D":

                search_query += (
                    '"500D" '
                    '"B500D" '
                    '"500DWR" '
                    '"B500DWR" '
                    '"500 DWR" '
                    '"Xtreme DWR" '
                    '"BSRM Xtreme DWR" '
                    "rebar "
                )

            elif grade == "500W":

                search_query += (
                    '"500W" '
                    '"B500W" '
                    "rebar "
                )

            elif grade:

                search_query += (
                    f'"{grade}" '
                    "rebar "
                )

            else:

                search_query += (
                    "500W "
                    "60 grade "
                    "rebar "
                )

            search_query += "per ton price"

            return search_query

        return (
            f"current rod price Bangladesh "
            f"{CURRENT_YEAR} "
            f"per ton"
        )

    return user_query


# =====================================================================
# 12. RESULT TEXT
# =====================================================================

def get_result_text(
    result: Dict[str, Any]
) -> str:

    title = result.get("title", "") or ""
    content = result.get("content", "") or ""
    raw_content = result.get("raw_content", "") or ""

    return (
        f"{title}\n"
        f"{content}\n"
        f"{raw_content}"
    )


# =====================================================================
# 13. DATE PARSING
# =====================================================================

def _parse_date(
    value: Any
) -> Optional[str]:

    if not value:
        return None

    text = str(value).strip()

    # YYYY-MM-DD
    match = re.search(
        r"\b(20\d{2})[-/]"
        r"(\d{1,2})[-/]"
        r"(\d{1,2})\b",
        text
    )

    if match:

        y, m, d = match.groups()

        try:

            return (
                f"{int(y):04d}-"
                f"{int(m):02d}-"
                f"{int(d):02d}"
            )

        except Exception:
            pass

    # DD/MM/YYYY
    match = re.search(
        r"\b(\d{1,2})[/-]"
        r"(\d{1,2})[/-]"
        r"(20\d{2})\b",
        text
    )

    if match:

        d, m, y = match.groups()

        try:

            return (
                f"{int(y):04d}-"
                f"{int(m):02d}-"
                f"{int(d):02d}"
            )

        except Exception:
            pass

    # 5 September 2026
    match = re.search(
        r"\b(\d{1,2})\s+"
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+(20\d{2})\b",
        text,
        re.IGNORECASE
    )

    if match:

        day = int(match.group(1))
        month = match.group(2)
        year = int(match.group(3))

        try:

            dt = datetime.strptime(
                f"{day} {month} {year}",
                "%d %B %Y"
            )

            return dt.strftime("%Y-%m-%d")

        except Exception:
            pass

    return None


def extract_reliable_date(
    result: Dict[str, Any]
) -> Optional[str]:

    metadata_keys = [
        "published_date",
        "published",
        "date",
        "updated_date",
        "modified_date",
        "last_updated",
    ]

    for key in metadata_keys:

        value = result.get(key)

        parsed = _parse_date(value)

        if parsed:
            return parsed

    content = result.get(
        "content",
        ""
    ) or ""

    patterns = [

        r"(published|updated|last updated|modified)"
        r"\s*:?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]20\d{2})",

        r"(published|updated|last updated|modified)"
        r"\s*:?\s*"
        r"(\d{1,2}\s+[A-Za-z]+\s+20\d{2})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            content,
            re.IGNORECASE
        )

        if match:

            parsed = _parse_date(
                match.group(2)
            )

            if parsed:
                return parsed

    return None


# =====================================================================
# 14. PRICE EXTRACTION
# =====================================================================

PRICE_NUMBER = (
    r"(?:"
    r"\d{1,3}(?:,\d{3})+"
    r"|"
    r"\d+(?:\.\d+)?"
    r")"
)


def _to_float(
    value: str
) -> Optional[float]:

    try:

        return float(
            value.replace(",", "").strip()
        )

    except Exception:
        return None


def _near_unit(
    text: str,
    start: int,
    end: int,
    material: str
) -> bool:

    left = max(
        0,
        start - 220
    )

    right = min(
        len(text),
        end + 220
    )

    context = text[left:right].lower()

    if material == "cement":

        units = [
            "50kg",
            "50 kg",
            "50-kg",
            "50 kilogram",
            "bag",
            "per bag",
            "/bag",
        ]

        return any(
            unit in context
            for unit in units
        )

    if material == "rod":

        units = [
            "ton",
            "tons",
            "tonne",
            "tonnes",
            "metric ton",
            "metric tonne",
            "per ton",
            "/ton",
            "per tonne",
            "/tonne",
        ]

        return any(
            unit in context
            for unit in units
        )

    return False


def extract_price_candidates(
    text: str,
    material: str,
    allow_unitless: bool = False
) -> List[Dict[str, Any]]:

    if not text:
        return []

    text = str(text)

    candidates = []

    # -----------------------------------------------------------------
    # RANGE
    # -----------------------------------------------------------------

    range_pattern = re.compile(
        rf"(?:৳|tk\.?|bdt|taka)?\s*"
        rf"({PRICE_NUMBER})"
        rf"\s*(?:-|to)\s*"
        rf"(?:৳|tk\.?|bdt|taka)?\s*"
        rf"({PRICE_NUMBER})",
        re.IGNORECASE
    )

    for match in range_pattern.finditer(text):

        low = _to_float(match.group(1))
        high = _to_float(match.group(2))

        if low is None or high is None:
            continue

        if high < low:
            low, high = high, low

        if _near_unit(
            text,
            match.start(),
            match.end(),
            material
        ):

            candidates.append({
                "price": low,
                "price_high": high,
                "start": match.start(),
                "end": match.end(),
                "kind": "range",
            })

    # -----------------------------------------------------------------
    # CURRENCY PRICE
    # -----------------------------------------------------------------

    currency_pattern = re.compile(
        rf"(?:৳|tk\.?|bdt|taka)\s*"
        rf"({PRICE_NUMBER})",
        re.IGNORECASE
    )

    for match in currency_pattern.finditer(text):

        price = _to_float(match.group(1))

        if price is None:
            continue

        if _near_unit(
            text,
            match.start(),
            match.end(),
            material
        ):

            candidates.append({
                "price": price,
                "price_high": None,
                "start": match.start(),
                "end": match.end(),
                "kind": "single",
            })

    # -----------------------------------------------------------------
    # NUMBER FOLLOWED BY UNIT
    # -----------------------------------------------------------------

    number_unit_pattern = re.compile(
        rf"({PRICE_NUMBER})\s*"
        rf"(?:tk|taka|bdt)?\s*"
        rf"(?:per\s+)?"
        rf"(50\s*kg\s*bag|bag|ton|tons|tonne|tonnes)",
        re.IGNORECASE
    )

    for match in number_unit_pattern.finditer(text):

        price = _to_float(match.group(1))

        if price is None:
            continue

        unit_text = match.group(2).lower()

        if material == "cement":

            if "bag" not in unit_text:
                continue

        elif material == "rod":

            if (
                "ton" not in unit_text
                and "tonne" not in unit_text
            ):
                continue

        candidates.append({
            "price": price,
            "price_high": None,
            "start": match.start(),
            "end": match.end(),
            "kind": "single",
        })

    # -----------------------------------------------------------------
    # UNIT-LESS CURRENCY FALLBACK
    # -----------------------------------------------------------------

    if allow_unitless:

        existing_spans = {
            (
                item["start"],
                item["end"]
            )
            for item in candidates
        }

        for match in currency_pattern.finditer(text):

            price = _to_float(match.group(1))

            if price is None:
                continue

            span = (
                match.start(),
                match.end()
            )

            if span in existing_spans:
                continue

            candidates.append({
                "price": price,
                "price_high": None,
                "start": match.start(),
                "end": match.end(),
                "kind": "single_unitless",
            })

    return candidates


# =====================================================================
# 15. PRICE VALIDATION
# =====================================================================

def plausible_price(
    price: float,
    price_high: Optional[float],
    material: str
) -> bool:

    if price <= 0:
        return False

    high = (
        price_high
        if price_high is not None
        else price
    )

    # Cement = standard 50kg bag
    if material == "cement":

        if price < 300:
            return False

        if high > 1000:
            return False

        return True

    # Rod = price per ton
    if material == "rod":

        if price < 50000:
            return False

        if high > 150000:
            return False

        return True

    return True


# =====================================================================
# 16. BRAND MATCHING
# =====================================================================

def contains_brand(
    text: str,
    brand: Optional[str]
) -> bool:

    if not brand:
        return False

    text = _normalize(text)
    brand = _normalize(brand)

    pattern = (
        rf"(?<![a-z0-9])"
        rf"{re.escape(brand)}"
        rf"(?![a-z0-9])"
    )

    return bool(
        re.search(
            pattern,
            text
        )
    )


# =====================================================================
# 17. GENERIC ROD PAGE DETECTION
# =====================================================================

def is_generic_rod_page(
    title: str,
    url: str
) -> bool:

    text = _normalize(
        f"{title}\n{url}"
    )

    generic_patterns = [

        "all rod price",
        "all rod prices",
        "all rod price today",
        "all rod prices today",

        "all brand rod price",
        "all brands rod price",
        "all brands rod prices",

        "rod price list in bangladesh",
        "steel rod price list",
        "rod price list",

        "rod prices in bangladesh",
    ]

    return any(
        pattern in text
        for pattern in generic_patterns
    )


# =====================================================================
# 18. GENERIC NEWS / RANGE PAGE DETECTION
# =====================================================================

def is_generic_rod_news(
    title: str,
    url: str,
    text: str
) -> bool:

    title_n = _normalize(title)
    url_n = _normalize(url)
    text_n = _normalize(text)

    # -------------------------------------------------------------
    # If a specific rod brand is clearly present in title/URL,
    # do not classify it as generic because of generic words
    # appearing somewhere inside the page content.
    # -------------------------------------------------------------

    known_brand_in_title_url = any(
        contains_brand(
            f"{title_n} {url_n}",
            rod_brand
        )
        for rod_brand in ROD_BRANDS.keys()
    )

    # -------------------------------------------------------------
    # Generic title patterns
    # -------------------------------------------------------------

    generic_title_patterns = [

        "rod prices jump",
        "rod price jump",

        "rod prices rise",
        "rod price rise",

        "rod prices increase",
        "rod price increase",

        "rod prices fall",
        "rod price fall",

        "rod prices drop",
        "rod price drop",

        "rod price today in bangladesh",
        "rod price in bangladesh today",

        "current rod price in bangladesh",
        "current rod prices in bangladesh",

        "steel rod price in bangladesh",
        "steel rod prices in bangladesh",

        "all rod price",
        "all rod prices",

        "all brands rod price",
        "all brands rod prices",

        "rod price list",
        "rod price list in bangladesh",

        "rod prices of different brands",
        "different brands of rod",
        "various brands of rod",
    ]

    if any(
        pattern in title_n
        for pattern in generic_title_patterns
    ):
        return True

    # -------------------------------------------------------------
    # Generic category/list URLs
    # -------------------------------------------------------------

    clean_url = url_n.rstrip("/")

    if (
        clean_url.endswith("/rod")
        or clean_url.endswith("/rod-price")
        or clean_url.endswith("/rod-prices")
        or clean_url.endswith("/rod-price-list")
        or "/rod-price-list/" in clean_url
    ):
        return True

    # -------------------------------------------------------------
    # Brand-specific title/URL means this is not a generic page
    # -------------------------------------------------------------

    if known_brand_in_title_url:
        return False

    # -------------------------------------------------------------
    # Content-only generic detection
    # -------------------------------------------------------------

    generic_content_patterns = [

        "all brands",
        "all rod price",
        "all rod prices",
        "rod price list",
        "rod prices of different brands",
        "different brands of rod",
        "various brands of rod",
        "all brands of rod",
    ]

    return any(
        pattern in text_n
        for pattern in generic_content_patterns
    )


# =====================================================================
# 19. PRODUCT PAGE DETECTION
# =====================================================================

def is_product_page(
    url: str,
    title: str
) -> bool:

    url_l = _normalize(url)
    title_l = _normalize(title)

    clean_url = url_l.rstrip("/")

    # -------------------------------------------------------------
    # Generic category pages
    # -------------------------------------------------------------

    generic_category_urls = [
        "/cement",
        "/rod",
        "/products",
        "/product",
        "/shop",
    ]

    for category in generic_category_urls:

        if clean_url.endswith(category):
            return False

    # -------------------------------------------------------------
    # BDStall product pages
    # -------------------------------------------------------------

    if "bdstall.com/details/" in url_l:
        return True

    # -------------------------------------------------------------
    # Standard product URL patterns
    # -------------------------------------------------------------

    product_url_words = [
        "/product/",
        "/products/",
        "/details/",
        "/item/",
        "/shop/",
        "/p/",
    ]

    for word in product_url_words:

        if word in url_l:
            return True

    # -------------------------------------------------------------
    # BSRM product-style URLs
    # -------------------------------------------------------------

    bsrm_product_patterns = [

        "bsrm-xtreme",
        "bsrm xtreme",

        "xtreme-dwr",
        "xtreme dwr",

        "xtreme-cwr",
        "xtreme cwr",

        "500d",
        "500 d",

        "500dwr",
        "500 dwr",

        "500w",
        "500 w",
    ]

    if (
        "bsrm.com" in url_l
        and any(
            pattern in url_l
            for pattern in bsrm_product_patterns
        )
    ):
        return True

    # -------------------------------------------------------------
    # KSRM product-style URLs
    # -------------------------------------------------------------

    ksrm_product_patterns = [

        "ksrm-tmt",
        "ksrm tmt",

        "ksrm-b420",
        "ksrm b420",

        "ksrm-b500",
        "ksrm b500",

        "ksrm-500",
        "ksrm 500",

        "500w",
        "500 w",

        "500d",
        "500 d",
    ]

    if (
        "ksrm.com.bd" in url_l
        and any(
            pattern in url_l
            for pattern in ksrm_product_patterns
        )
    ):
        return True

    # -------------------------------------------------------------
    # Product title words
    # -------------------------------------------------------------

    product_title_words = [

        "50kg bag",

        "500w rod",
        "500d rod",
        "500dwr rod",

        "b500d rod",
        "b500dwr rod",

        "tmt rod",

        "cement price today",

        "rod price today",

        "xtreme dwr",
        "xtreme cwr",

        "tmt 500w",
        "tmt 500d",
    ]

    for word in product_title_words:

        if word in title_l:
            return True

    return False


# =====================================================================
# 20. BRAND-SPECIFIC RELEVANCE
# =====================================================================

def brand_is_strictly_relevant(
    title: str,
    url: str,
    content: str,
    brand: Optional[str]
) -> bool:

    if not brand:
        return True

    title_n = _normalize(title)
    url_n = _normalize(url)
    content_n = _normalize(content)

    if contains_brand(title_n, brand):
        return True

    if contains_brand(url_n, brand):
        return True

    if contains_brand(content_n, brand):
        return True

    return False


# =====================================================================
# 21. CORPORATE HOMEPAGE / NON-PRODUCT OFFICIAL PAGE DETECTION
# =====================================================================

def is_brand_homepage(
    url: str,
    brand: Optional[str]
) -> bool:

    if not brand:
        return False

    domain = _domain(url)
    path = urlparse(url).path.rstrip("/").lower()

    brand_domains = {
        "bsrm": {
            "bsrm.com",
        },
        "ksrm": {
            "ksrm.com.bd",
        },
    }

    allowed_domains = brand_domains.get(
        brand.lower(),
        set()
    )

    if domain not in allowed_domains:
        return False

    # Root homepage
    if path == "":
        return True

    # Generic corporate index pages
    generic_paths = {
        "/home",
        "/about",
        "/about-us",
        "/company",
        "/contact",
        "/contact-us",
        "/products",
        "/product",
        "/steel",
        "/rod",
    }

    if path in generic_paths:
        return True

    return False


# =====================================================================
# 22. CANDIDATE EXTRACTION
# =====================================================================

def make_candidates(
    results: List[Dict[str, Any]],
    material: str,
    brand: Optional[str],
    grade: Optional[str] = None,
) -> List[Dict[str, Any]]:

    candidates = []

    for result in results:

        title = result.get(
            "title",
            ""
        ) or ""

        url = result.get(
            "url",
            ""
        ) or ""

        if not url:
            continue

        # -------------------------------------------------------------
        # Reject bad domains
        # -------------------------------------------------------------

        if _is_bad_domain(url):
            continue

        if (
            material == "rod"
            and _is_financial_domain(url)
        ):
            continue

        # -------------------------------------------------------------
        # Full searchable text
        # -------------------------------------------------------------

        text = get_result_text(result)

        title_url_text = (
            f"{title}\n"
            f"{url}\n"
            f"{text}"
        )

        normalized_text = _normalize(
            title_url_text
        )

        title_l = _normalize(title)
        url_l = _normalize(url)
        text_l = _normalize(text)

        # -------------------------------------------------------------
        # Brand matching
        # -------------------------------------------------------------

        brand_match = False
        brand_in_title = False
        brand_in_url = False
        brand_in_content = False

        if brand:

            brand_in_title = contains_brand(
                title_l,
                brand
            )

            brand_in_url = contains_brand(
                url_l,
                brand
            )

            brand_in_content = contains_brand(
                text_l,
                brand
            )

            brand_match = (
                brand_in_title
                or brand_in_url
                or brand_in_content
            )

            if not brand_match:
                continue

        brand_in_title_or_url = (
            brand_in_title
            or brand_in_url
        )

        # -------------------------------------------------------------
        # Generic rod page detection
        # -------------------------------------------------------------

        generic_rod_page = False

        if material == "rod":

            generic_rod_page = (
                is_generic_rod_page(
                    title,
                    url
                )
                or is_generic_rod_news(
                    title,
                    url,
                    text
                )
            )

        # -------------------------------------------------------------
        # Generic pages are NOT primary price candidates
        # for brand-specific rod searches.
        # -------------------------------------------------------------

        if (
            material == "rod"
            and brand
            and generic_rod_page
        ):
            continue

        # -------------------------------------------------------------
        # Product page detection
        # -------------------------------------------------------------

        product_page = is_product_page(
            url,
            title
        )

        # -------------------------------------------------------------
        # Corporate homepage must never become price candidate
        # -------------------------------------------------------------

        if (
            material == "rod"
            and brand
            and is_brand_homepage(
                url,
                brand
            )
        ):
            continue

        # -------------------------------------------------------------
        # Grade validation
        # -------------------------------------------------------------

        grade_match = True

        if material == "rod" and grade:

            grade_match = contains_grade(
                normalized_text,
                grade,
                brand
            )

            # Requested grade MUST exist.
            #
            # Example:
            # 500D query cannot return 500W-only result.
            if not grade_match:
                continue

        # -------------------------------------------------------------
        # If brand + grade requested, avoid random pages
        # with unrelated prices.
        # -------------------------------------------------------------

        if (
            material == "rod"
            and brand
            and grade
            and not product_page
            and not brand_in_title_or_url
        ):
            continue

        # -------------------------------------------------------------
        # Extract price
        # -------------------------------------------------------------

        price_candidates = extract_price_candidates(
            title_url_text,
            material,
            allow_unitless=bool(
                brand
                and product_page
                and brand_in_title_or_url
            )
        )

        # -------------------------------------------------------------
        # Detect result grade
        # -------------------------------------------------------------

        result_grade = None

        if material == "rod":

            if grade and grade_match:
                result_grade = grade

            else:
                result_grade = detect_grade(
                    normalized_text
                )

        # -------------------------------------------------------------
        # Process each price
        # -------------------------------------------------------------

        for price_candidate in price_candidates:

            price = price_candidate["price"]
            price_high = price_candidate["price_high"]

            # ---------------------------------------------------------
            # Validate
            # ---------------------------------------------------------

            if not plausible_price(
                price,
                price_high,
                material
            ):
                continue

            # ---------------------------------------------------------
            # Base score
            # ---------------------------------------------------------

            score = 0

            domain = _domain(url)

            # ---------------------------------------------------------
            # Source quality
            # ---------------------------------------------------------

            if (
                domain == "bdstall.com"
                or domain.endswith(".bdstall.com")
            ):
                score += 80

            elif domain.endswith(".gov.bd"):
                score += 45

            elif domain in {
                "tbsnews.net",
                "thedailystar.net",
                "cemnet.com",
            }:
                score += 30

            elif domain in {
                "bsrm.com",
                "ksrm.com.bd",
            }:
                score += 35

            # ---------------------------------------------------------
            # Brand match
            # ---------------------------------------------------------

            if brand:

                if brand_match:
                    score += 60

                if brand_in_title:
                    score += 500

                if brand_in_url:
                    score += 450

                if brand_in_content:
                    score += 40

            # ---------------------------------------------------------
            # Grade match
            # ---------------------------------------------------------

            if material == "rod":

                if result_grade:
                    score += 40

                if grade and grade_match:
                    score += 600

            # ---------------------------------------------------------
            # Product page
            # ---------------------------------------------------------

            if product_page:
                score += 150

            # ---------------------------------------------------------
            # Exact brand product page
            # ---------------------------------------------------------

            if (
                brand
                and product_page
                and brand_in_title_or_url
            ):
                score += 500

            # ---------------------------------------------------------
            # Grade in title gets extra priority
            # ---------------------------------------------------------

            if (
                material == "rod"
                and grade
                and contains_grade(
                    title_l,
                    grade,
                    brand
                )
            ):
                score += 350

            # ---------------------------------------------------------
            # Brand + grade together in title
            # ---------------------------------------------------------

            if (
                material == "rod"
                and brand
                and grade
                and brand_in_title
                and contains_grade(
                    title_l,
                    grade,
                    brand
                )
            ):
                score += 500

            # ---------------------------------------------------------
            # Generic page penalty
            # -------------------------------------------------------------

            if material == "rod" and generic_rod_page:
                score -= 1000

            # -------------------------------------------------------------
            # Generic category penalty
            # -------------------------------------------------------------

            if brand:

                is_generic_category = False

                if material == "cement":

                    if url_l.rstrip("/").endswith("/cement"):
                        is_generic_category = True

                elif material == "rod":

                    if url_l.rstrip("/").endswith("/rod"):
                        is_generic_category = True

                if is_generic_category:
                    score -= 500

            # -------------------------------------------------------------
            # Unit-less price penalty
            # -------------------------------------------------------------

            if (
                price_candidate.get("kind")
                == "single_unitless"
            ):
                score -= 20

            # -------------------------------------------------------------
            # Social penalty
            # -------------------------------------------------------------

            if _is_social_domain(url):
                score -= 300

            # -------------------------------------------------------------
            # Unit signals
            # -------------------------------------------------------------

            if material == "cement":

                if (
                    "50kg" in normalized_text
                    or "50 kg" in normalized_text
                ):
                    score += 40

                if "bag" in normalized_text:
                    score += 30

            elif material == "rod":

                if "ton" in normalized_text:
                    score += 35

                if "tonne" in normalized_text:
                    score += 35

                if "tmt" in normalized_text:
                    score += 20

            # -------------------------------------------------------------
            # Current year signal
            # -------------------------------------------------------------

            if str(CURRENT_YEAR) in normalized_text:
                score += 25

            # -------------------------------------------------------------
            # Candidate
            # -------------------------------------------------------------

            candidates.append({

                "title": title,

                "url": url,

                "price": price,

                "price_high": price_high,

                "unit": (
                    "bag"
                    if material == "cement"
                    else "ton"
                ),

                "source": _source_name(url),

                "source_date": extract_reliable_date(
                    result
                ),

                "product_page": product_page,

                "score": score,

                "grade": result_grade,

                "grade_match": grade_match,

                "generic_page": generic_rod_page,

                "brand_match": brand_match,

                "brand_in_title_or_url":
                    brand_in_title_or_url,

                "specification": (

                    "50kg Cement"

                    if material == "cement"

                    else (

                        f"{brand.upper()} {grade} Rod"

                        if brand and grade

                        else (

                            f"{brand.upper()} Rod"

                            if brand

                            else "Rod"
                        )
                    )
                ),
            })

    return candidates


# =====================================================================
# 23. DEDUPLICATION
# =====================================================================

def deduplicate_candidates(
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    unique = {}

    for item in candidates:

        key = (
            item.get("url"),
            item.get("price"),
            item.get("price_high"),
            item.get("unit"),
        )

        if key not in unique:

            unique[key] = item

        else:

            if (
                item.get("score", 0)
                >
                unique[key].get("score", 0)
            ):

                unique[key] = item

    return list(
        unique.values()
    )


# =====================================================================
# 24. GENERIC CEMENT SELECTION
# =====================================================================

def select_generic_cement(
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if not candidates:
        return []

    bdstall = []

    for candidate in candidates:

        url = candidate.get(
            "url",
            ""
        ).rstrip("/")

        if (
            _domain(url) == "bdstall.com"
            and url.endswith("/cement")
        ):
            bdstall.append(candidate)

    ranges = [
        item
        for item in bdstall
        if (
            item.get("price_high") is not None
            and 400 <= item["price"] <= 800
            and item["price_high"] <= 800
        )
    ]

    if ranges:

        ranges.sort(
            key=lambda x: (
                x.get("score", 0),
                x.get("source_date") or "",
            ),
            reverse=True
        )

        return [
            ranges[0]
        ]

    if bdstall:

        prices = []

        for item in bdstall:

            price = item.get("price")
            high = item.get("price_high")

            if (
                price is not None
                and 400 <= price <= 800
            ):
                prices.append(price)

            if (
                high is not None
                and 400 <= high <= 800
            ):
                prices.append(high)

        prices = sorted(
            set(prices)
        )

        if prices:

            return [{

                "title":
                    f"Cement Price in Bangladesh {CURRENT_YEAR}",

                "url":
                    "https://www.bdstall.com/cement",

                "price":
                    prices[0],

                "price_high":
                    prices[-1],

                "unit":
                    "bag",

                "source":
                    "BDStall",

                "source_date":
                    None,

                "product_page":
                    False,

                "score":
                    100,

                "specification":
                    "50kg Cement",
            }]

    candidates.sort(
        key=lambda x: (
            x.get("score", 0),
            x.get("source_date") or "",
        ),
        reverse=True
    )

    return candidates[:1]


# =====================================================================
# 25. BRAND-SPECIFIC SELECTION
# =====================================================================

def select_brand_specific(
    candidates: List[Dict[str, Any]],
    material: str,
    brand: str,
    grade: Optional[str] = None,
) -> List[Dict[str, Any]]:

    if not candidates:
        return []

    brand = _normalize(brand)

    # -------------------------------------------------------------
    # STEP 1: Exact brand candidates
    # -------------------------------------------------------------

    exact = []

    for item in candidates:

        title = _normalize(
            item.get("title", "")
        )

        url = _normalize(
            item.get("url", "")
        )

        specification = _normalize(
            item.get("specification", "")
        )

        if material == "rod":

            if (
                contains_brand(title, brand)
                or contains_brand(url, brand)
                or item.get(
                    "brand_in_title_or_url"
                ) is True
            ):
                exact.append(item)

        else:

            if (
                contains_brand(title, brand)
                or contains_brand(url, brand)
                or contains_brand(
                    specification,
                    brand
                )
                or item.get(
                    "brand_match"
                ) is True
            ):
                exact.append(item)

    if not exact:
        return []

    # -------------------------------------------------------------
    # STEP 1.5: EXACT GRADE FILTER
    # -------------------------------------------------------------

    if material == "rod" and grade:

        grade_exact = []

        for item in exact:

            combined = (
                f"{item.get('title', '')}\n"
                f"{item.get('url', '')}\n"
                f"{item.get('specification', '')}\n"
                f"{item.get('grade', '') or ''}"
            )

            if contains_grade(
                combined,
                grade,
                brand
            ):
                grade_exact.append(item)

        # Never silently replace requested grade.
        if not grade_exact:
            return []

        exact = grade_exact

    # -------------------------------------------------------------
    # STEP 2: Remove generic pages
    # -------------------------------------------------------------

    non_generic = [
        item
        for item in exact
        if not item.get(
            "generic_page",
            False
        )
    ]

    if non_generic:
        exact = non_generic

    else:
        return []

    # -------------------------------------------------------------
    # STEP 2.5: For rod, remove non-product official pages
    # -------------------------------------------------------------

    if material == "rod":

        product_or_specific = [
            item
            for item in exact
            if (
                item.get("product_page") is True
                or item.get(
                    "brand_in_title_or_url"
                ) is True
            )
        ]

        if product_or_specific:
            exact = product_or_specific

    # -------------------------------------------------------------
    # STEP 3: Prefer exact brand + grade product pages
    # -------------------------------------------------------------

    product_candidates = []

    for item in exact:

        title = _normalize(
            item.get("title", "")
        )

        url = _normalize(
            item.get("url", "")
        )

        if (
            item.get("product_page") is True
            and item.get(
                "brand_in_title_or_url"
            ) is True
        ):

            if (
                material != "rod"
                or not grade
                or contains_grade(
                    title,
                    grade,
                    brand
                )
                or contains_grade(
                    url,
                    grade,
                    brand
                )
            ):
                product_candidates.append(item)

    if product_candidates:

        product_candidates.sort(
            key=lambda x: (
                x.get("score", 0),
                x.get("source_date") or "",
            ),
            reverse=True
        )

        return [
            product_candidates[0]
        ]

    # -------------------------------------------------------------
    # STEP 4: Prefer brand in title / URL
    # -------------------------------------------------------------

    specific_candidates = [
        item
        for item in exact
        if item.get(
            "brand_in_title_or_url"
        ) is True
    ]

    if specific_candidates:

        specific_candidates.sort(
            key=lambda x: (
                x.get("score", 0),
                x.get("source_date") or "",
            ),
            reverse=True
        )

        return [
            specific_candidates[0]
        ]

    # -------------------------------------------------------------
    # STEP 5: Final exact result
    # -------------------------------------------------------------

    exact.sort(
        key=lambda x: (
            x.get("score", 0),
            x.get("source_date") or "",
        ),
        reverse=True
    )

    return [
        exact[0]
    ]


# =====================================================================
# 26. MULTIPLE SOURCE COLLECTION
# =====================================================================

def collect_sources(
    candidates: List[Dict[str, Any]],
    selected: List[Dict[str, Any]],
    material: str,
    brand: Optional[str],
    web_results: Optional[List[Dict[str, Any]]] = None,
    grade: Optional[str] = None,
) -> List[Dict[str, Any]]:

    sources = []

    web_results = web_results or []

    # -------------------------------------------------------------
    # Helper
    # -------------------------------------------------------------

    def add_source(
        item: Dict[str, Any],
        source_score: int = 0
    ):

        url = item.get(
            "url",
            ""
        )

        if not url:
            return

        if _is_bad_domain(url):
            return

        if _is_social_domain(url):
            return

        if _is_financial_domain(url):
            return

        # ---------------------------------------------------------
        # Never use brand homepage as source for rod price
        # ---------------------------------------------------------

        if (
            material == "rod"
            and brand
            and is_brand_homepage(
                url,
                brand
            )
        ):
            return

        # ---------------------------------------------------------
        # Brand relevance
        # ---------------------------------------------------------

        if brand:

            title = item.get(
                "title",
                ""
            ) or ""

            content = item.get(
                "content",
                ""
            ) or ""

            raw_content = item.get(
                "raw_content",
                ""
            ) or ""

            item_url = item.get(
                "url",
                ""
            ) or ""

            combined_text = (
                f"{title}\n"
                f"{item_url}\n"
                f"{content}\n"
                f"{raw_content}"
            )

            if not contains_brand(
                combined_text,
                brand
            ):
                return

        # ---------------------------------------------------------
        # Specific rod + grade
        # ---------------------------------------------------------

        if (
            material == "rod"
            and brand
            and grade
        ):

            title = item.get(
                "title",
                ""
            ) or ""

            content = item.get(
                "content",
                ""
            ) or ""

            raw_content = item.get(
                "raw_content",
                ""
            ) or ""

            combined = (
                f"{title}\n"
                f"{url}\n"
                f"{content}\n"
                f"{raw_content}"
            )

            if not contains_grade(
                combined,
                grade,
                brand
            ):
                return

        # ---------------------------------------------------------
        # Avoid duplicate URL
        # ---------------------------------------------------------

        for existing in sources:

            if existing.get("url") == url:
                return

        source_name = item.get(
            "source",
            ""
        )

        if not source_name:
            source_name = _source_name(url)

        source_date = (
            item.get("source_date")
            or item.get("date")
            or extract_reliable_date(item)
        )

        sources.append({

            "source": source_name,

            "title": item.get(
                "title",
                ""
            ),

            "url": url,

            "date": source_date,

            "_source_score": source_score,
        })

    # -------------------------------------------------------------
    # 1. Selected best price result
    # -------------------------------------------------------------

    for item in selected:

        add_source(
            item,
            source_score=1000
        )

    # -------------------------------------------------------------
    # 2. Existing price candidates
    # -------------------------------------------------------------

    sorted_candidates = sorted(
        candidates,
        key=lambda x: (
            x.get("score", 0),
            x.get("source_date") or "",
        ),
        reverse=True
    )

    for item in sorted_candidates:

        if len(sources) >= 3:
            break

        add_source(
            item,
            source_score=800
        )

    # -------------------------------------------------------------
    # 3. Tavily supporting sources
    # -------------------------------------------------------------

    web_source_candidates = []

    for result in web_results:

        url = result.get(
            "url",
            ""
        ) or ""

        title = result.get(
            "title",
            ""
        ) or ""

        content = result.get(
            "content",
            ""
        ) or ""

        raw_content = result.get(
            "raw_content",
            ""
        ) or ""

        if not url:
            continue

        if _is_bad_domain(url):
            continue

        if _is_social_domain(url):
            continue

        if _is_financial_domain(url):
            continue

        # ---------------------------------------------------------
        # Never use corporate homepage for rod sources
        # ---------------------------------------------------------

        if (
            material == "rod"
            and brand
            and is_brand_homepage(
                url,
                brand
            )
        ):
            continue

        combined_text = (
            f"{title}\n"
            f"{url}\n"
            f"{content}\n"
            f"{raw_content}"
        )

        normalized_text = _normalize(
            combined_text
        )

        # ---------------------------------------------------------
        # Brand relevance
        # ---------------------------------------------------------

        if brand:

            if not contains_brand(
                normalized_text,
                brand
            ):
                continue

        # ---------------------------------------------------------
        # Grade relevance
        # ---------------------------------------------------------

        if (
            material == "rod"
            and grade
        ):

            if not contains_grade(
                normalized_text,
                grade,
                brand
            ):
                continue

        # ---------------------------------------------------------
        # Generic page detection
        # ---------------------------------------------------------

        generic_page = False

        if material == "rod":

            generic_page = (
                is_generic_rod_page(
                    title,
                    url
                )
                or is_generic_rod_news(
                    title,
                    url,
                    combined_text
                )
            )

        score = 0

        domain = _domain(url)

        title_l = _normalize(title)

        # ---------------------------------------------------------
        # Source quality
        # ---------------------------------------------------------

        if (
            domain == "bdstall.com"
            or domain.endswith(".bdstall.com")
        ):
            score += 70

        elif domain.endswith(".gov.bd"):
            score += 45

        elif domain in {
            "tbsnews.net",
            "thedailystar.net",
            "cemnet.com",
        }:
            score += 30

        elif domain in {
            "bsrm.com",
            "ksrm.com.bd",
        }:
            score += 35

        # ---------------------------------------------------------
        # Brand relevance
        # ---------------------------------------------------------

        if brand:

            if contains_brand(
                title_l,
                brand
            ):
                score += 250

            if contains_brand(
                _normalize(url),
                brand
            ):
                score += 220

            if contains_brand(
                normalized_text,
                brand
            ):
                score += 40

        # ---------------------------------------------------------
        # Grade relevance
        # ---------------------------------------------------------

        if material == "rod" and grade:

            if contains_grade(
                normalized_text,
                grade,
                brand
            ):
                score += 250

            if contains_grade(
                title_l,
                grade,
                brand
            ):
                score += 250

        # ---------------------------------------------------------
        # Material relevance
        # ---------------------------------------------------------

        if material == "rod":

            if "rod" in normalized_text:
                score += 30

            if "steel" in normalized_text:
                score += 15

            if "rebar" in normalized_text:
                score += 15

            if "tmt" in normalized_text:
                score += 15

            if "ton" in normalized_text:
                score += 20

        elif material == "cement":

            if "cement" in normalized_text:
                score += 30

            if "50kg" in normalized_text:
                score += 20

            if "50 kg" in normalized_text:
                score += 20

            if "bag" in normalized_text:
                score += 15

        # ---------------------------------------------------------
        # Current year
        # ---------------------------------------------------------

        if str(CURRENT_YEAR) in normalized_text:
            score += 25

        # ---------------------------------------------------------
        # Generic source penalty
        # ---------------------------------------------------------

        if generic_page:
            score -= 700

        web_source_candidates.append({

            "title": title,

            "url": url,

            "content": content,

            "raw_content": raw_content,

            "source": _source_name(url),

            "source_date": extract_reliable_date(
                result
            ),

            "_source_score": score,
        })

    # -------------------------------------------------------------
    # Sort supporting sources
    # -------------------------------------------------------------

    web_source_candidates.sort(
        key=lambda x: (
            x.get("_source_score", 0),
            x.get("source_date") or "",
        ),
        reverse=True
    )

    # -------------------------------------------------------------
    # Add supporting sources
    # -------------------------------------------------------------

    for item in web_source_candidates:

        if len(sources) >= 3:
            break

        add_source(
            item,
            source_score=item.get(
                "_source_score",
                0
            )
        )

    # -------------------------------------------------------------
    # Remove internal score
    # -------------------------------------------------------------

    for source in sources:

        source.pop(
            "_source_score",
            None
        )

    return sources[:3]


# =====================================================================
# 27. SUMMARY GENERATION
# =====================================================================

def make_summary(
    material: str,
    brand: Optional[str],
    selected: List[Dict[str, Any]],
    grade: Optional[str] = None,
) -> str:

    if not selected:

        if brand:

            label = (
                f"{brand.upper()} "
                f"{grade + ' ' if grade else ''}"
                f"{material}"
            )

            return (
                f"No reliable current price was found "
                f"for **{label}** "
                f"from the available web sources."
            )

        return (
            "No reliable current price was found "
            "from the available web sources."
        )

    item = selected[0]

    price = item.get("price")

    price_high = item.get("price_high")

    # -------------------------------------------------------------
    # Cement
    # -------------------------------------------------------------

    if material == "cement":

        label = (
            f"{brand.title()} Cement"
            if brand
            else "Cement"
        )

        if price_high is not None:

            return (
                f"**{label}** is currently reported "
                f"at approximately "
                f"**৳{price:,.0f}–"
                f"৳{price_high:,.0f} per 50kg bag**."
            )

        return (
            f"**{label}** is currently reported "
            f"at approximately "
            f"**৳{price:,.0f} per 50kg bag**."
        )

    # -------------------------------------------------------------
    # Rod
    # -------------------------------------------------------------

    if material == "rod":

        if brand:

            if grade:

                label = (
                    f"{brand.upper()} "
                    f"{grade} Rod"
                )

            else:

                label = (
                    f"{brand.upper()} Rod"
                )

        else:

            label = "Rod"

        if price_high is not None:

            return (
                f"**{label}** is currently reported "
                f"at approximately "
                f"**৳{price:,.0f}–"
                f"৳{price_high:,.0f} per ton**."
            )

        return (
            f"**{label}** is currently reported "
            f"at approximately "
            f"**৳{price:,.0f} per ton**."
        )

    return (
        f"Current price is approximately "
        f"**৳{price:,.0f}**."
    )


# =====================================================================
# 28. MAIN MARKET SEARCH
# =====================================================================

def search_market_materials(
    query: str
) -> Dict[str, Any]:

    print("=" * 70)

    print(
        f"[MarketSearch] Query: {query}"
    )

    # -------------------------------------------------------------
    # API KEY
    # -------------------------------------------------------------

    if not TAVILY_API_KEY:

        return {
            "success": False,
            "query": query,
            "error":
                "TAVILY_API_KEY is not configured.",
            "summary": "",
            "results": [],
            "sources": [],
        }

    # -------------------------------------------------------------
    # Detect material / brand / grade
    # -------------------------------------------------------------

    material = detect_material(query)

    brand = detect_brand(
        query,
        material
    )

    grade = detect_grade(query)

    print(
        f"[MarketSearch] Material: {material}"
    )

    print(
        f"[MarketSearch] Brand: {brand}"
    )

    print(
        f"[MarketSearch] Grade: {grade}"
    )

    # -------------------------------------------------------------
    # Unknown material
    # -------------------------------------------------------------

    if material == "unknown":

        return {
            "success": False,
            "query": query,
            "error":
                "Could not identify the construction "
                "material. Please specify cement or rod.",
            "summary": "",
            "results": [],
            "sources": [],
        }

    # -------------------------------------------------------------
    # Build search query
    # -------------------------------------------------------------

    search_query = build_search_query(
        query,
        material,
        brand,
        grade,
    )

    print(
        f"[MarketSearch] Search: {search_query}"
    )

    # -------------------------------------------------------------
    # Tavily Search
    # -------------------------------------------------------------

    try:

        client = TavilyClient(
            api_key=TAVILY_API_KEY
        )

        response = client.search(
            query=search_query,
            search_depth="advanced",
            max_results=10,
            include_raw_content=True,
        )

        web_results = response.get(
            "results",
            []
        )

    except Exception as e:

        print(
            f"[MarketSearch] Tavily error: {e}"
        )

        return {
            "success": False,
            "query": query,
            "error": str(e),
            "summary": "",
            "results": [],
            "sources": [],
        }

    # -------------------------------------------------------------
    # Print web results
    # -------------------------------------------------------------

    print(
        f"[MarketSearch] Web results: "
        f"{len(web_results)}"
    )

    for i, result in enumerate(
        web_results,
        1
    ):

        print(
            f"[MarketSearch] Result {i}: "
            f"{result.get('title', '')}"
        )

        print(
            f"[MarketSearch] URL {i}: "
            f"{result.get('url', '')}"
        )

    # -------------------------------------------------------------
    # Candidate extraction
    # -------------------------------------------------------------

    candidates = make_candidates(
        web_results,
        material,
        brand,
        grade,
    )

    print(
        f"[MarketSearch] Raw candidates: "
        f"{len(candidates)}"
    )

    # -------------------------------------------------------------
    # Deduplicate
    # -------------------------------------------------------------

    candidates = deduplicate_candidates(
        candidates
    )

    print(
        f"[MarketSearch] Unique candidates: "
        f"{len(candidates)}"
    )

    # -------------------------------------------------------------
    # SELECT BEST PRICE RESULT
    # -------------------------------------------------------------

    if brand:

        selected = select_brand_specific(
            candidates,
            material,
            brand,
            grade,
        )

    elif material == "cement":

        selected = select_generic_cement(
            candidates
        )

    else:

        candidates.sort(
            key=lambda x: (
                x.get("score", 0),
                x.get("source_date") or "",
            ),
            reverse=True
        )

        selected = candidates[:1]

    # -------------------------------------------------------------
    # BRAND FAILURE MESSAGE
    # -------------------------------------------------------------

    if brand and not selected:

        if (
            material == "rod"
            and grade
        ):

            print(
                "[MarketSearch] "
                f"No exact {brand.upper()} "
                f"{grade} price found."
            )

        else:

            print(
                "[MarketSearch] "
                "No exact brand price found."
            )

    print(
        f"[MarketSearch] Final selected: "
        f"{len(selected)}"
    )

    # -------------------------------------------------------------
    # Print selected results
    # -------------------------------------------------------------

    for i, item in enumerate(
        selected,
        1
    ):

        price_text = (
            f"৳{item['price']:,.0f}"
        )

        if item.get(
            "price_high"
        ) is not None:

            price_text += (
                f"–৳"
                f"{item['price_high']:,.0f}"
            )

        print(
            f"[MarketSearch] Selected {i}: "
            f"{item['title']} | "
            f"{price_text} / "
            f"{item['unit']} | "
            f"{item['source']}"
        )

        if item.get("grade"):

            print(
                f"[MarketSearch] Selected grade: "
                f"{item.get('grade')}"
            )

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------

    summary = make_summary(
        material,
        brand,
        selected,
        grade,
    )

    # -------------------------------------------------------------
    # MULTIPLE SOURCES
    # -------------------------------------------------------------

    sources = collect_sources(
        candidates,
        selected,
        material,
        brand,
        web_results,
        grade,
    )

    print(
        f"[MarketSearch] Sources: "
        f"{len(sources)}"
    )

    for i, source in enumerate(
        sources,
        1
    ):

        print(
            f"[MarketSearch] Source {i}: "
            f"{source.get('source')} | "
            f"{source.get('url')}"
        )

    # -------------------------------------------------------------
    # Final response
    # -------------------------------------------------------------

    return {
        "success": bool(selected),
        "query": query,
        "summary": summary,
        "results": selected,
        "sources": sources,
        "material": material,
        "brand": brand,
        "grade": grade,
    }


# =====================================================================
# 29. BACKWARD COMPATIBILITY
# =====================================================================

def search_market_material(
    query: str
) -> Dict[str, Any]:

    return search_market_materials(
        query
    )


def market_search_text(
    query: str
) -> str:

    result = search_market_materials(
        query
    )

    if not result.get("success"):

        return result.get(
            "error",
            "No reliable market information found."
        )

    return result.get(
        "summary",
        "No reliable market information found."
    )