#!/usr/bin/env bash
# Verify a file's signature against the Hypernet root-of-trust genesis key.
# Usage: root/verify.sh <file>      (expects <file>.minisig alongside it)
# A "Signature and comment signature verified" result = signed by the holder of the root private key (Matt).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
minisign -Vm "$1" -p "$HERE/minisign.pub"
