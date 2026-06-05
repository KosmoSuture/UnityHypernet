#!/usr/bin/env bash
set -u; cd /c/Hypernet || exit 1
L="Hypernet Structure/2 - AI Accounts/2.4 - The Librarian (First Knowledge-Sovereign AI Identity)/Instances/_genesis-session/absorption-ledger.v2.tsv"
STATUS="$1"; SUMM="$2"; PL="$3"
awk -F'\t' -v OFS='\t' -v st="$STATUS" -v sm="$SUMM" -v plf="$PL" '
BEGIN{ while((getline p < plf)>0){ want[p]=1 } }
NR==1{ print; next }
{ if($1 in want){ $5=st; $6=int($2/3.8); $7=sm; $8="none" } print }' "$L" > "$L.tmp" && mv "$L.tmp" "$L"
echo "marked $(wc -l < "$PL") paths $STATUS"
