# -*- coding: utf-8 -*-
"""
URL Feature Extraction Module
Produces 16 features used by the trained Random Forest / XGBoost model.
"""

from urllib.parse import urlparse
import ipaddress
import re
import urllib.request
import urllib.parse
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# ─── 1. Address-bar based features ────────────────────────────────────────────

def havingIP(url: str) -> int:
    """Checks if URL contains an IP address (1 = phishing)."""
    try:
        host = urlparse(url).netloc
        ipaddress.ip_address(host)
        return 1
    except ValueError:
        return 0


def haveAtSign(url: str) -> int:
    """Checks for '@' symbol in URL (1 = phishing)."""
    return 1 if "@" in url else 0


def getLength(url: str) -> int:
    """URL length >= 54 → phishing (1)."""
    return 1 if len(url) >= 54 else 0


def getDepth(url: str) -> int:
    """Count path depth (number of '/' segments)."""
    segments = urlparse(url).path.split('/')
    return sum(1 for s in segments if s)


def redirection(url: str) -> int:
    """Checks for suspicious '//' in URL path (1 = phishing)."""
    pos = url.rfind('//')
    if pos > 7:
        return 1
    return 0


def httpDomain(url: str) -> int:
    """Checks if 'https' appears in domain part (1 = phishing)."""
    domain = urlparse(url).netloc
    return 1 if 'https' in domain else 0


_SHORTENING_SERVICES = re.compile(
    r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl"
    r"|tr\.im|is\.gd|cli\.gs|yfrog\.com|migre\.me|ff\.im|tiny\.cc"
    r"|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|short\.to"
    r"|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com"
    r"|fic\.kr|loopt\.us|doiop\.com|short\.ie|kl\.am|wp\.me"
    r"|rubyurl\.com|om\.ly|to\.ly|bit\.do|lnkd\.in|db\.tt|qr\.ae"
    r"|adf\.ly|bitly\.com|cur\.lv|tinyurl\.com|ity\.im|q\.gs"
    r"|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com"
    r"|cutt\.us|u\.bb|yourls\.org|prettylinkpro\.com|scrnch\.me"
    r"|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd"
    r"|link\.zip\.net"
)


def tinyURL(url: str) -> int:
    """Checks for URL shortening services (1 = phishing)."""
    return 1 if _SHORTENING_SERVICES.search(url) else 0


def prefixSuffix(url: str) -> int:
    """Checks for '-' in domain (1 = phishing)."""
    return 1 if '-' in urlparse(url).netloc else 0


# ─── 2. Domain based features ─────────────────────────────────────────────────

def web_traffic(url: str) -> int:
    """Estimates web traffic rank (1 = low-rank / phishing)."""
    try:
        encoded = urllib.parse.quote(url)
        soup = BeautifulSoup(
            urllib.request.urlopen(
                f"http://data.alexa.com/data?cli=10&dat=s&url={encoded}", timeout=5
            ).read(),
            "xml",
        )
        rank = int(soup.find("REACH")["RANK"])
        return 1 if rank < 100_000 else 0
    except Exception:
        return 1


def domainAge(domain_name) -> int:
    """Age of domain < 6 months → phishing (1)."""
    try:
        creation_date = domain_name.creation_date
        expiration_date = domain_name.expiration_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        if creation_date is None or expiration_date is None:
            return 1
        if isinstance(creation_date, str):
            creation_date = datetime.strptime(creation_date, "%Y-%m-%d")
        if isinstance(expiration_date, str):
            expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
        age_months = abs((expiration_date - creation_date).days) / 30
        return 1 if age_months < 6 else 0
    except Exception:
        return 1


def domainEnd(domain_name) -> int:
    """Remaining domain time < 6 months → phishing (1)."""
    try:
        expiration_date = domain_name.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        if expiration_date is None:
            return 1
        if isinstance(expiration_date, str):
            expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
        remaining_months = abs((expiration_date - datetime.now()).days) / 30
        return 0 if remaining_months >= 6 else 1
    except Exception:
        return 1


# ─── 3. HTML & JS based features ──────────────────────────────────────────────

def iframe(response) -> int:
    if response == "" or response is None:
        return 1
    return 0 if re.findall(r"[<iframe>|<frameBorder>]", response.text) else 1


def mouseOver(response) -> int:
    if response == "" or response is None:
        return 1
    return 1 if re.findall("<script>.+onmouseover.+</script>", response.text) else 0


def rightClick(response) -> int:
    if response == "" or response is None:
        return 1
    return 0 if re.findall(r"event.button ?== ?2", response.text) else 1


def forwarding(response) -> int:
    if response == "" or response is None:
        return 1
    return 0 if len(response.history) <= 2 else 1


# ─── 4. Main extraction function ──────────────────────────────────────────────

FEATURE_NAMES = [
    "Have_IP", "Have_At", "URL_Length", "URL_Depth", "Redirection",
    "https_Domain", "TinyURL", "Prefix_Suffix", "DNS_Record", "Web_Traffic",
    "Domain_Age", "Domain_End", "iFrame", "Mouse_Over", "Right_Click", "Web_Forwards",
]


def extract_features(url: str) -> list:
    """
    Extract all 16 features from a URL and return as a plain Python list.
    Missing/error features default to 1 (conservative = phishing).
    """
    features = []

    # Address-bar features (8)
    features.append(havingIP(url))
    features.append(haveAtSign(url))
    features.append(getLength(url))
    features.append(getDepth(url))
    features.append(redirection(url))
    features.append(httpDomain(url))
    features.append(tinyURL(url))
    features.append(prefixSuffix(url))

    # Domain-based features (4)  — whois optional
    dns = 0
    domain_name = None
    try:
        import whois  # optional dependency
        domain_name = whois.whois(urlparse(url).netloc)
    except Exception:
        dns = 1

    features.append(dns)
    features.append(web_traffic(url))
    features.append(1 if dns else domainAge(domain_name))
    features.append(1 if dns else domainEnd(domain_name))

    # HTML & JS features (4)
    try:
        response = requests.get(url, timeout=8, allow_redirects=True)
    except Exception:
        response = None

    features.append(iframe(response))
    features.append(mouseOver(response))
    features.append(rightClick(response))
    features.append(forwarding(response))

    return features
