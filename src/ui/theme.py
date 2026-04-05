"""Centralized theme configuration for the UI"""

# ============================================================================
## COLOR SCHEME
# ============================================================================

COLORS = {
    # Backgrounds
    "bg_main": "#EEF2F6",
    "bg_panel": "#F8FAFC",
    "bg_white": "#FFFFFF",
    "bg_light": "#E7EDF3",
    "bg_input": "#F8FAFC",
    
    # Borders
    "border": "#D8E0E8",
    "border_light": "#DCE4EC",
    
    # Text
    "text_dark": "#1E2A33",
    "text_muted": "#5F6E7C",
    "text_light": "#8A98A6",
    "text_lighter": "#A8B3BD",
    "text_button": "#2B3A44",
    
    # Accents
    "accent_dark": "#35586E",
    "accent_hover": "#2F4F63",
    "accent_teal": "#4A8F93",
    "accent_teal_hover": "#3F7F83",
    
    # Status colors
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
}

# ============================================================================
## FONT SIZES
# ============================================================================

FONT_SIZES = {
    "header": 36,
    "title": 20,
    "label": 18,
    "body": 17,
    "small": 15,
    "xsmall": 10,
}

# ============================================================================
## CHART COLORS
# ============================================================================

# Year colors for performance charts
YEAR_COLORS = {
    2026: "#FF8C42",  # Orange
    2025: "#4A90E2",  # Blue
    2024: "#50C878",  # Green
    2023: "#9E9E9E",  # Grey
    2022: "#9C27B0",  # Purple
}

# ============================================================================
## MODE CONFIGURATION
# ============================================================================

MODE_CONFIG = {
    "12nc": {
        "key": "12nc",
        "display": "12NC",
        "title": "12NC Component Analysis",
        "description": "Search and analyze component performance, belonging relationships, and demand forecasts",
        "items": [],  # Will be populated from loaded CBOM data
    },
    "room": {
        "key": "room",
        "display": "Room",
        "title": "Room Performance Analysis",
        "description": "Analyze room performance metrics, deployed components, and predict future demand",
        "items": [],  # Will be populated from loaded CBOM data
    },
}

# ============================================================================
## GRANULARITY MAPPING
# ============================================================================

# Map UI granularities to analyzer granularities
GRANULARITY_MAP = {
    "Months": "monthly",
    "Quarters": "quarterly",
    "Years": "yearly"
}

# Maximum periods for each granularity
GRANULARITY_PERIODS = {
    "Months": 12,
    "Quarters": 4,
    "Years": 3
}
