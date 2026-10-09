"""Central settings for the whole project.

Everything you may want to change lives here or in the .env file:
model name, cache lifetimes, pricing, and the list of companies the team supports.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# ---- LLM settings (read from .env) -------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
# gemini-2.5-flash is stable and works with the code as-is. Newer Gemini generations
# use different "thinking" options, so test a new model before relying on it.
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash").strip()

# ---- Folders and cache -------------------------------------------------------------
CACHE_DIR = ROOT / ".cache"
LOG_DIR = ROOT / "logs"
FINANCIALS_TTL_HOURS = float(os.getenv("FINANCIALS_TTL_HOURS", "24"))
NEWS_TTL_HOURS = float(os.getenv("NEWS_TTL_HOURS", "1"))

# ---- Team behaviour ----------------------------------------------------------------
MAX_RETRIES = 1          # supervisor retries a failed agent once, then marks it unavailable
PEERS_PER_COMPANY = 2

# ---- Cost estimate: USD per 1 million tokens (input, output) ------------------------
# Check https://ai.google.dev/gemini-api/docs/pricing and edit when prices change.
PRICING_USD_PER_1M = {
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
}
DEFAULT_PRICING = (0.30, 2.50)


# ---- Supported companies -----------------------------------------------------------
def _c(name, ticker, sector, *aliases, note=None):
    return {"name": name, "ticker": ticker, "sector": sector, "aliases": list(aliases), "note": note}


IT, BANK, AUTO = "Information Technology", "Banking", "Automobile"
FMCG, ENERGY, PHARMA = "FMCG", "Energy", "Pharma"
METALS, CEMENT, POWER, NBFC = "Metals", "Cement", "Power", "NBFC & Financial Services"

TATA_MOTORS_NOTE = (
    "Tata Motors demerged on 1 Oct 2025: TMPV is the passenger-vehicle arm (including Jaguar Land Rover) "
    "and TMCV holds trucks and buses. Data providers may mix pre- and post-demerger periods, "
    "so compare these two with care."
)

# Order matters: peers are picked from the top of each sector's list (roughly by size).
UNIVERSE = [
    _c("Tata Consultancy Services", "TCS.NS", IT, "tcs", "tata consultancy"),
    _c("Infosys", "INFY.NS", IT, "infy"),
    _c("HCL Technologies", "HCLTECH.NS", IT, "hcl tech", "hcl", "hcltech"),
    _c("Wipro", "WIPRO.NS", IT),
    _c("Tech Mahindra", "TECHM.NS", IT, "tech m"),

    _c("HDFC Bank", "HDFCBANK.NS", BANK, "hdfc"),
    _c("ICICI Bank", "ICICIBANK.NS", BANK, "icici"),
    _c("State Bank of India", "SBIN.NS", BANK, "sbi"),
    _c("Kotak Mahindra Bank", "KOTAKBANK.NS", BANK, "kotak", "kotak bank"),
    _c("Axis Bank", "AXISBANK.NS", BANK, "axis"),

    _c("Maruti Suzuki", "MARUTI.NS", AUTO, "maruti"),
    _c("Mahindra & Mahindra", "M&M.NS", AUTO, "m&m", "mahindra", "mahindra and mahindra"),
    _c("Tata Motors Passenger Vehicles", "TMPV.NS", AUTO, "tata motors", "tata motors pv",
       "tata motors passenger", "tmpv", "jlr", "jaguar land rover", note=TATA_MOTORS_NOTE),
    _c("Tata Motors (Commercial Vehicles)", "TMCV.NS", AUTO, "tata motors cv", "tata motors commercial",
       "tmcv", note=TATA_MOTORS_NOTE),
    _c("Bajaj Auto", "BAJAJ-AUTO.NS", AUTO),
    _c("Eicher Motors", "EICHERMOT.NS", AUTO, "eicher", "royal enfield"),
    _c("Hero MotoCorp", "HEROMOTOCO.NS", AUTO, "hero"),
    _c("Ashok Leyland", "ASHOKLEY.NS", AUTO),

    _c("Hindustan Unilever", "HINDUNILVR.NS", FMCG, "hul"),
    _c("ITC", "ITC.NS", FMCG),
    _c("Nestle India", "NESTLEIND.NS", FMCG, "nestle"),
    _c("Britannia Industries", "BRITANNIA.NS", FMCG, "britannia"),
    _c("Tata Consumer Products", "TATACONSUM.NS", FMCG, "tata consumer"),

    _c("Reliance Industries", "RELIANCE.NS", ENERGY, "reliance", "ril"),
    _c("ONGC", "ONGC.NS", ENERGY, "oil and natural gas corporation"),
    _c("Indian Oil Corporation", "IOC.NS", ENERGY, "ioc", "indian oil"),
    _c("Bharat Petroleum", "BPCL.NS", ENERGY, "bpcl"),

    _c("Sun Pharmaceutical", "SUNPHARMA.NS", PHARMA, "sun pharma"),
    _c("Dr. Reddy's Laboratories", "DRREDDY.NS", PHARMA, "dr reddys", "dr reddy"),
    _c("Cipla", "CIPLA.NS", PHARMA),
    _c("Divi's Laboratories", "DIVISLAB.NS", PHARMA, "divis labs", "divis"),

    _c("Tata Steel", "TATASTEEL.NS", METALS),
    _c("JSW Steel", "JSWSTEEL.NS", METALS),
    _c("Hindalco Industries", "HINDALCO.NS", METALS, "hindalco"),
    _c("Vedanta", "VEDL.NS", METALS, "vedl"),

    _c("UltraTech Cement", "ULTRACEMCO.NS", CEMENT, "ultratech"),
    _c("Grasim Industries", "GRASIM.NS", CEMENT, "grasim"),
    _c("Ambuja Cements", "AMBUJACEM.NS", CEMENT, "ambuja"),
    _c("Shree Cement", "SHREECEM.NS", CEMENT),

    _c("NTPC", "NTPC.NS", POWER),
    _c("Power Grid Corporation", "POWERGRID.NS", POWER, "powergrid"),
    _c("Tata Power", "TATAPOWER.NS", POWER),

    _c("Bajaj Finance", "BAJFINANCE.NS", NBFC),
    _c("Bajaj Finserv", "BAJAJFINSV.NS", NBFC),
    _c("Cholamandalam Investment and Finance", "CHOLAFIN.NS", NBFC, "chola"),
    _c("Shriram Finance", "SHRIRAMFIN.NS", NBFC, "shriram"),
]

# Hand-picked peers where "first two in the sector" would be a poor match.
PEER_OVERRIDES = {
    "TMCV.NS": ["ASHOKLEY.NS", "EICHERMOT.NS"],
    "TMPV.NS": ["MARUTI.NS", "M&M.NS"],
    "MARUTI.NS": ["M&M.NS", "BAJAJ-AUTO.NS"],
}

# Warnings added to the note when ratios behave differently for a sector.
SECTOR_CAVEATS = {
    BANK: "For banks, debt/equity and operating margin are not meaningful; focus on ROE and P/E.",
    NBFC: "For lenders, debt/equity is structurally high and operating margin is not meaningful; focus on ROE and P/E.",
}
