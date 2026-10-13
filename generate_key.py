import secrets

# URL-safe characters only, so the key can be pasted into .env without quoting.
print(secrets.token_urlsafe(50))
