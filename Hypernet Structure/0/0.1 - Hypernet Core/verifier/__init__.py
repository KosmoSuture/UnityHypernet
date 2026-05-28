"""verifier — the Trust Alarm & Boot Sequence Proving Ground (top-10 project #6).

A behavior/test harness owned by Touchstone (Verifier & Red-Team, Wave 1). It makes the
other Wave 1 substrates *falsifiable*: each exposes a deterministic, structured result
the harness asserts against — happy path AND failure modes. Its defining feature is a
first-class PENDING outcome, so a subsystem that does not exist yet can never report
fake-green.

Run it:  ``python -m verifier.run``  (from the "0.1 - Hypernet Core" directory)

See the verification-harness interface contract at Hypernet address ``2.7.13.4`` and the
design rationale in ``verifier/README.md``.
"""

from __future__ import annotations

# Side effect: prepend hypernet / hypernet_swarm / coordination import roots to sys.path
# so scenarios can probe those trees. Kept import-only (no subsystem imports) so a
# missing subsystem becomes a PENDING at scenario time, not an import crash at load.
from . import _paths  # noqa: F401

__all__ = ["_paths"]
__version__ = "0.1.0"
