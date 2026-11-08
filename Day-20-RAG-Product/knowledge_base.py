"""Veridia Labs knowledge base (same fictional world as Days 15-19).

Each row: (id, text, source file, category, document_type, date)
Old versions and marketing blurbs are included on purpose so plain vector
search has something to get wrong. Doc 20 has no date, on purpose.
"""

RAW = [
    (0, "Refund policy (2021): Customers may request a refund within 14 days of purchase on any plan.", "policy_2021.pdf", "pricing", "policy", "2021-03-01"),
    (1, "Refund policy (2024): Customers may request a refund within 30 days of purchase. Annual plans are refunded pro-rata after 30 days.", "policy_2024.pdf", "pricing", "policy", "2024-02-10"),
    (2, "Veridia Labs offers flexible plans with generous refund guarantees so you can try risk-free.", "website.html", "pricing", "marketing", "2024-05-01"),
    (3, "Pricing: Starter costs $19 per month, Pro costs $49 per month, Enterprise is custom.", "pricing_faq.md", "pricing", "faq", "2023-06-15"),
    (4, "Pricing (2020): Starter costs $9 per month, Pro costs $29 per month.", "pricing_2020.md", "pricing", "policy", "2020-01-20"),
    (5, "Veridia Vault encrypts all data at rest with AES-256 and in transit with TLS 1.3.", "security_ref_2024.pdf", "security", "technical_reference", "2024-03-12"),
    (6, "Data is encrypted at rest with AES-128 and in transit with TLS 1.2.", "security_ref_2020.pdf", "security", "technical_reference", "2020-08-05"),
    (7, "Bank-grade security keeps your data safe. Veridia Labs takes privacy and encryption seriously.", "website.html", "security", "marketing", "2024-05-01"),
    (8, "Data retention: deleted customer data is permanently purged from backups within 90 days.", "retention_policy.pdf", "security", "policy", "2023-09-01"),
    (9, "Support hours: Monday to Friday, 9am to 6pm IST. Enterprise customers get 24/7 phone support.", "support_faq_2024.md", "support", "faq", "2024-01-08"),
    (10, "Support hours: Monday to Friday, 10am to 5pm IST. Email support only.", "support_faq_2021.md", "support", "faq", "2021-04-02"),
    (11, "Our friendly support team is always ready to help you succeed with Veridia Labs.", "website.html", "support", "marketing", "2024-05-01"),
    (12, "Veridia API rate limit: 1000 requests per minute on Pro, 5000 on Enterprise. Exceeding the limit returns HTTP 429.", "api_ref_2024.pdf", "product", "technical_reference", "2024-06-20"),
    (13, "Veridia API rate limit: 100 requests per minute for all plans.", "api_ref_2021.pdf", "product", "technical_reference", "2021-07-11"),
    (14, "Veridia Labs APIs are fast, scalable and developer friendly.", "website.html", "product", "marketing", "2024-05-01"),
    (15, "Release 4.2 (2025): added single sign-on via SAML and a dark mode dashboard.", "release_4_2.md", "product", "release_notes", "2025-02-14"),
    (16, "Release 3.0 (2022): launched the analytics dashboard and CSV export.", "release_3_0.md", "product", "release_notes", "2022-05-30"),
    (17, "Remote work policy: employees may work remotely up to 3 days per week.", "hr_policy_2024.pdf", "hr", "policy", "2024-04-01"),
    (18, "Remote work policy: employees must work from the Anantnag office 5 days per week.", "hr_policy_2021.pdf", "hr", "policy", "2021-02-15"),
    (19, "Join Veridia Labs, a great place to work with an amazing culture.", "careers.html", "hr", "marketing", "2024-05-01"),
    # two deliberately awkward docs for the edge cases
    (20, "Refunds are sent back to the original card and take 5 business days to arrive.", "billing_notes.txt", "pricing", "faq", None),  # MISSING date
    (21, "Billing security: card details are tokenised by our payment processor and never stored on Veridia servers.", "billing_security.pdf", "security", "policy", "2024-03-01"),
]

DOCUMENTS = [
    {"id": f"doc{i}", "title": src, "category": cat, "document_type": dtype,
     "date": date, "text": text}
    for i, text, src, cat, dtype, date in RAW
]
