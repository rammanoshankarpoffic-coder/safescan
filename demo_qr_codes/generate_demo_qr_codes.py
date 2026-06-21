"""
Generates a set of QR code images for demoing SafeScan.
Covers LOW, MEDIUM, and HIGH risk cases across UPI and URL payload types.

Run: python generate_demo_qr_codes.py
Output: PNG files in ./output/
"""

import qrcode
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# (filename, payload, expected_risk, description)
test_cases = [
    (
        "1_safe_upi_payment.png",
        "upi://pay?pa=ramesh.stores@oksbi&pn=Ramesh General Stores&am=250.00&cu=INR",
        "LOW",
        "Legitimate-looking UPI payment — proper VPA, real payee name, valid amount",
    ),
    (
        "2_safe_known_site.png",
        "https://www.paytm.com/",
        "LOW",
        "Official, well-formed HTTPS link to a known payment brand",
    ),
    (
        "3_suspicious_shortener.png",
        "https://bit.ly/3xPayNow",
        "MEDIUM",
        "URL shortener — real destination is hidden from the user",
    ),
    (
        "4_suspicious_upi_no_name.png",
        "upi://pay?pa=9988776655@paytm&pn=&am=5000.00&cu=INR",
        "MEDIUM",
        "UPI request with a large amount and no payee name shown",
    ),
    (
        "5_fake_typosquat_domain.png",
        "https://paytm-secure-verify.com/refund/claim",
        "MEDIUM",
        "Typosquat / brand impersonation — contains 'paytm' but is not the real domain. "
        "One strong signal on its own; combine with other flags (no HTTPS, IP address, etc.) to push into HIGH.",
    ),
    (
        "5b_fake_typosquat_plus_no_https.png",
        "http://paytm-secure-verify.xyz/refund/claim",
        "HIGH",
        "Same impersonation as above, plus no HTTPS and a high-risk TLD — multiple compounding red flags",
    ),
    (
        "6_fake_ip_address_link.png",
        "http://192.168.45.12/upi/pay?amount=9999",
        "HIGH",
        "Raw IP address instead of a domain, plus no HTTPS — classic phishing pattern",
    ),
    (
        "7_fake_malformed_upi.png",
        "upi://pay?pa=12345&pn=&am=0",
        "HIGH",
        "Malformed UPI ID, missing payee name, invalid amount",
    ),
    (
        "8_plain_text.png",
        "Welcome to Ramesh General Stores! Visit again.",
        "LOW",
        "Harmless plain text QR (e.g. a poster or menu) — not a payment at all",
    ),
]

print("Generating demo QR codes...\n")

for filename, payload, expected_risk, description in test_cases:
    img = qrcode.make(payload, box_size=10, border=4)
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path)
    print(f"✓ {filename}")
    print(f"   Payload: {payload}")
    print(f"   Expected risk: {expected_risk}")
    print(f"   Why: {description}\n")

print(f"All {len(test_cases)} QR codes saved to ./{OUTPUT_DIR}/")
