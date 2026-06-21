# Demo QR Codes — Usage Guide

9 QR code images in `output/`, covering a spread of risk levels you can
scan live during your demo or presentation.

## Suggested demo order (tells a story, low risk → high risk)

| # | File | Risk | What it shows |
|---|------|------|----------------|
| 1 | `1_safe_upi_payment.png` | LOW (100) | Clean UPI payment — start here to show what "safe" looks like |
| 2 | `2_safe_known_site.png` | LOW (100) | Real Paytm link — shows it doesn't just flag everything |
| 3 | `3_suspicious_shortener.png` | MEDIUM (70) | Shortened link — destination hidden |
| 4 | `4_suspicious_upi_no_name.png` | MEDIUM (70) | ₹5,000 request, no payee name shown |
| 5 | `5_fake_typosquat_domain.png` | MEDIUM (55) | Fake Paytm domain — one strong red flag |
| 5b | `5b_fake_typosquat_plus_no_https.png` | HIGH (10) | Same fake domain + no HTTPS + bad TLD — **strongest demo case, save for last** |
| 6 | `6_fake_ip_address_link.png` | HIGH (25) | Raw IP address link — classic phishing |
| 7 | `7_fake_malformed_upi.png` | HIGH (35) | Broken/fake UPI request |
| 8 | `8_plain_text.png` | LOW (80) | Harmless text QR — shows the app isn't payment-only |

## How to actually demo this live

1. Display these QR codes on a **second screen or printed paper** —
   don't try to scan them off the same phone you're demoing on.
   Easiest: open the images on a laptop screen, scan that with your phone.
2. Start with case 1 (clean payment) to set the baseline — "here's what
   safe looks like."
3. Then jump straight to **5b** (the compound fake-Paytm case) — it's your
   strongest, most visually convincing HIGH-risk result with three stacked
   reasons. This is the moment that should land with judges.
4. If you have time, show 1-2 more in between to demonstrate range
   (shortener, malformed UPI).

## If you want to test with your own fake examples live

You don't have to only use these 9. You can write any UPI string or URL
into a QR generator on the spot (e.g. https://www.qr-code-generator.com/)
to respond to judge questions like "what if it looked like this instead?"
— a good way to show the engine isn't just memorized answers.
