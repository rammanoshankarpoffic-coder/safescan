"""
SafeScan Risk Engine
---------------------
Rule-based fraud detection for scanned QR code payloads.

Takes the raw decoded text of a QR code and returns a structured
risk verdict: risk level, score, and human-readable reasons.

No external API calls required — fully self-contained heuristics,
so it works offline and demos reliably.
"""

import re
from urllib.parse import urlparse, parse_qs


# ---------------------------------------------------------------------------
# Reference data (in a real product this would be a live/curated database)
# ---------------------------------------------------------------------------

KNOWN_PAYMENT_DOMAINS = {
    "paytm.com",
    "phonepe.com",
    "razorpay.com",
    "okaxis",
    "oksbi",
    "okhdfcbank",
    "okicici",
    "ybl",  # PhonePe UPI handle suffix
    "upi",
    "gpay.app.goo.gl",
    "google.co.in",
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "rebrand.ly", "shorturl.at", "cutt.ly",
}

KNOWN_UPI_BANK_SUFFIXES = {
    "ybl", "ibl", "axl", "oksbi", "okhdfcbank", "okicici", "okaxis",
    "apl", "icici", "hdfcbank", "sbi", "axisbank", "kotak", "paytm",
    "upi",
}

SUSPICIOUS_TLDS = {".xyz", ".top", ".club", ".info", ".tk", ".click", ".online"}

# Brand names that are commonly impersonated in payment phishing
IMPERSONATED_BRANDS = ["paytm", "phonepe", "googlepay", "gpay", "upi", "sbi", "hdfc", "icici", "axis"]


# ---------------------------------------------------------------------------
# Payload classification
# ---------------------------------------------------------------------------

def classify_payload(payload: str) -> str:
    """Determine what kind of QR payload this is."""
    payload = payload.strip()
    if payload.lower().startswith("upi://"):
        return "upi"
    if payload.lower().startswith("http://") or payload.lower().startswith("https://"):
        return "url"
    return "text"


# ---------------------------------------------------------------------------
# UPI payload analysis
# ---------------------------------------------------------------------------

def analyze_upi(payload: str):
    """
    UPI deep links look like:
    upi://pay?pa=merchant@bank&pn=Merchant Name&am=100.00&cu=INR
    """
    reasons = []
    score = 100

    parsed = urlparse(payload)
    params = parse_qs(parsed.query)

    pa = params.get("pa", [""])[0]  # payee address (VPA)
    pn = params.get("pn", [""])[0]  # payee name
    am = params.get("am", [""])[0]  # amount

    # Check VPA format: should be name@bankhandle
    if not pa or "@" not in pa:
        reasons.append("UPI ID (VPA) is missing or malformed")
        score -= 40
    else:
        handle = pa.split("@")[-1].lower()
        if handle not in KNOWN_UPI_BANK_SUFFIXES:
            reasons.append(f"UPI handle '@{handle}' is not a recognized bank/payment handle")
            score -= 30

    # Check payee name presence
    am_value = None
    if am:
        try:
            am_value = float(am)
        except ValueError:
            am_value = None

    if not pn or pn.strip() == "":
        if am_value is not None and am_value >= 1000:
            reasons.append(
                f"Payee name is missing on a request for ₹{am_value:,.2f} — "
                "large unnamed requests are a common scam pattern"
            )
            score -= 30
        else:
            reasons.append("Payee name is missing — cannot verify who you're paying")
            score -= 15
    elif pn.strip().isdigit():
        reasons.append("Payee name looks like a number, not a real merchant name")
        score -= 15

    # Sanity check amount field if present
    if am:
        if am_value is None:
            reasons.append("Payment amount field is not a valid number")
            score -= 10
        elif am_value <= 0:
            reasons.append("Payment amount is zero or invalid")
            score -= 10

    if not reasons:
        reasons.append("UPI payment details look properly formatted")

    return max(score, 0), reasons


# ---------------------------------------------------------------------------
# URL payload analysis
# ---------------------------------------------------------------------------

def levenshtein(a: str, b: str) -> int:
    """Small edit-distance helper for typosquat detection."""
    if len(a) < len(b):
        return levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev_row = range(len(b) + 1)
    for i, ca in enumerate(a):
        curr_row = [i + 1]
        for j, cb in enumerate(b):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (ca != cb)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def analyze_url(payload: str):
    reasons = []
    score = 100

    parsed = urlparse(payload)
    domain = parsed.netloc.lower()
    domain_root = domain.split(":")[0]  # strip port if present

    # HTTPS check
    if parsed.scheme != "https":
        reasons.append("Link does not use HTTPS — connection is not encrypted")
        score -= 25

    # IP address instead of domain name
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain_root):
        reasons.append("Destination is a raw IP address, not a real domain — common phishing tactic")
        score -= 35

    # URL shortener check
    if domain_root in URL_SHORTENERS:
        reasons.append(f"Link uses a URL shortener ({domain_root}) — real destination is hidden")
        score -= 30

    # Suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if domain_root.endswith(tld):
            reasons.append(f"Domain uses an uncommon/high-risk extension ('{tld}') often used in scam sites")
            score -= 20
            break

    # Typosquat / brand impersonation check.
    # Split the domain's first label into chunks (on hyphens) so we catch
    # patterns like "paytrn-secure.xyz" (typo'd brand + extra word) and
    # "paytm-secure.xyz" (real brand name + extra word), not just exact matches.
    first_label = domain_root.split(".")[0]
    label_chunks = first_label.split("-")

    typosquat_flagged = False
    for brand in IMPERSONATED_BRANDS:
        is_known_domain = any(domain_root == d or domain_root.endswith("." + d) for d in KNOWN_PAYMENT_DOMAINS)

        if is_known_domain:
            continue

        # Exact brand name present as a chunk, but domain isn't the real one
        if brand in label_chunks:
            reasons.append(f"Domain contains '{brand}' but is not an official {brand} domain — likely impersonation")
            score -= 45
            typosquat_flagged = True
            break

        # Near-miss typosquat: any chunk is a slight misspelling of the brand
        for chunk in label_chunks:
            dist = levenshtein(chunk, brand)
            if 0 < dist <= 2 and len(chunk) >= 4:
                reasons.append(f"Domain segment '{chunk}' closely resembles trusted brand '{brand}' — possible typosquat")
                score -= 35
                typosquat_flagged = True
                break
        if typosquat_flagged:
            break

    # Excessive subdomains (another common obfuscation tactic)
    if domain_root.count(".") >= 3:
        reasons.append("URL uses an unusually long/nested domain structure — possible obfuscation")
        score -= 15

    if not reasons:
        reasons.append("No suspicious patterns detected in this URL")

    return max(score, 0), reasons


# ---------------------------------------------------------------------------
# Plain text payload
# ---------------------------------------------------------------------------

def analyze_text(payload: str):
    reasons = ["This QR code contains plain text, not a payment or link — generally low risk, but verify context"]
    return 80, reasons


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_qr(payload: str) -> dict:
    payload = payload.strip()
    payload_type = classify_payload(payload)

    if payload_type == "upi":
        score, reasons = analyze_upi(payload)
    elif payload_type == "url":
        score, reasons = analyze_url(payload)
    else:
        score, reasons = analyze_text(payload)

    if score >= 75:
        risk_level = "LOW"
    elif score >= 45:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "payload": payload,
        "payload_type": payload_type,
        "trust_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
    }


# ---------------------------------------------------------------------------
# Quick manual test when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_cases = [
        "upi://pay?pa=merchant@oksbi&pn=Ramesh Stores&am=250.00&cu=INR",
        "upi://pay?pa=12345&pn=&am=0",
        "https://paytm.com/pay/12345",
        "http://192.168.45.12/payment",
        "https://bit.ly/3xfake",
        "https://paytrn-secure.xyz/pay?id=12345",
        "https://paytm-secure-verify.com/pay",
        "Hello, this is just a text QR code",
    ]
    for case in test_cases:
        result = analyze_qr(case)
        print(f"\nPayload: {case}")
        print(f"Type: {result['payload_type']} | Score: {result['trust_score']} | Risk: {result['risk_level']}")
        for r in result["reasons"]:
            print(f"  - {r}")
