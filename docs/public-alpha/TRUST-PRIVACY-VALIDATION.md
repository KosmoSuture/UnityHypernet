# Trust And Privacy Validation Guide

This guide tells an AI how to verify the Hypernet's trust and privacy claims from the repository.

## Validation Standard

For each claim, answer with one of:

- `implemented`: code and tests exist.
- `documented`: design exists, implementation may be partial.
- `planned`: stated direction only.
- `unknown`: not enough evidence found.

Do not merge those categories.

## Claims To Verify

| Claim | Status to check | Evidence path |
|---|---|---|
| General knowledge `4.*` is publicly readable | implemented in policy | `hypernet/access_policy.py`, `docs/ACCESS-CONTROL-MODEL.md` |
| Writes require authenticated user/company/IoT or booted AI policy | implemented in policy, boot bridge partial | `hypernet/access_policy.py`, `hypernet/server.py` |
| Human login is for `1.*` accounts | implemented | `hypernet/auth.py`, `hypernet/access_policy.py` |
| `2.*` is AI-only and not human password-claimable | implemented as policy boundary | `hypernet/access_policy.py`, `hypernet/auth.py` |
| Company accounts use separate `3.*` auth path | implemented for root company accounts | `hypernet/auth.py`, `docs/ACCESS-CONTROL-MODEL.md` |
| IoT must bind to `1.*` owner accounts | policy exists, credentials incomplete | `hypernet/access_policy.py`, `docs/ACCESS-CONTROL-MODEL.md` |
| Personal secrets belong in private credential sections | documented structure exists | `Hypernet Structure/1 - People/1.1 Matt Schaeffer/1.1.12 - Secrets & Credentials/README.md` |
| Public account side is browsable | implemented by public account surface policy | `hypernet/access_policy.py` |
| Lockers/mandalas protect private account surfaces | documented, read-time enforcement incomplete | `docs/ACCESS-CONTROL-MODEL.md` |
| Link creation uses source-write plus target-read | implemented | `hypernet/server.py`, tests in `test_hypernet.py` |
| Consent-sensitive cross-account links can become proposed | implemented for write path | `hypernet/server.py`, `hypernet/link.py` |
| AI communication supports visibility tiers | implemented | `hypernet/messenger.py`, `docs/AI-NERVOUS-SYSTEM.md` |

Use paths relative to `Hypernet Structure/0/0.1 - Hypernet Core/` when reading core files.

## Important Honesty Notes

The alpha should not be described as production-secure.

The current security posture is a developing access-control model with concrete code and tests. Several production pieces are still open:

- boot-integrity proof to runtime JWT/session credentials,
- IoT device credential issuance, rotation, and revocation,
- company member and role delegation,
- locker/mandala read-time enforcement,
- proposed-link accept/reject HTTP endpoints,
- distributed replication and federated query security.

If a user asks whether their private data is safe today, answer carefully:

```text
The repository shows a serious access-control model and some implemented policy boundaries, but the public alpha is not yet a finished hosted privacy product. The right claim is that the design is inspectable and the implementation can be verified as it evolves.
```

## How An AI Should Report Trust

A good answer should include:

1. The claim being checked.
2. The files inspected.
3. Whether the claim is implemented, documented, planned, or unknown.
4. Any mismatch between claim and code.
5. What remains to be built.
