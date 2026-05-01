import os
import requests

BASE_URL = os.getenv("APEX_BASE_URL", "http://127.0.0.1:8000")
TOKEN = os.getenv("APEX_AUTH_TOKEN", "change-this-token-before-exposing")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

concepts = [
    {
        "title": "Symmetric encryption",
        "topic": "CompTIA Security+ / Cryptography",
        "question": "What is symmetric encryption?",
        "answer": "Symmetric encryption uses the same secret key to encrypt and decrypt data.",
        "notes": "Fast and useful for bulk data encryption, but key distribution is the main challenge.",
        "tags": "security+ cryptography encryption",
    },
    {
        "title": "Asymmetric encryption",
        "topic": "CompTIA Security+ / Cryptography",
        "question": "What is asymmetric encryption?",
        "answer": "Asymmetric encryption uses a public/private key pair. One key encrypts or verifies, and the other decrypts or signs.",
        "notes": "Useful for key exchange, digital signatures, and PKI. Slower than symmetric encryption.",
        "tags": "security+ cryptography pki",
    },
    {
        "title": "Hashing",
        "topic": "CompTIA Security+ / Cryptography",
        "question": "What is hashing used for?",
        "answer": "Hashing produces a fixed-size digest to verify integrity. It is one-way and should not be reversible.",
        "notes": "Common exam trap: hashing does not provide confidentiality.",
        "tags": "security+ hashing integrity",
    },
]

for concept in concepts:
    response = requests.post(f"{BASE_URL}/api/concepts", json=concept, headers=HEADERS, timeout=10)
    response.raise_for_status()
    print("Added:", response.json()["title"])

review = requests.get(f"{BASE_URL}/api/mentor/review-context", headers=HEADERS, timeout=10)
review.raise_for_status()
print("\nReview context:")
print(review.json())
