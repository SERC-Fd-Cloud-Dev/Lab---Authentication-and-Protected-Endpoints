"""LOCAL TEACHING FIXTURE ONLY: creates test tokens, never a web login endpoint."""
import argparse
from datetime import datetime, timedelta, timezone
import jwt
from auth import JWT_SECRET, ISSUER, AUDIENCE

parser = argparse.ArgumentParser()
parser.add_argument("--subject", default="u1")
parser.add_argument("--expired", action="store_true")
parser.add_argument("--scope", default="")
args = parser.parse_args()
now = datetime.now(timezone.utc)
claims = {"sub": args.subject, "iss": ISSUER, "aud": AUDIENCE,
          "iat": now, "exp": now + timedelta(minutes=-1 if args.expired else 30)}
if args.scope:
    claims["scope"] = args.scope
print(jwt.encode(claims, JWT_SECRET, algorithm="HS256"))
