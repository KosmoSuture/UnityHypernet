"""Address collision audit tool for TASK-057."""
import os
import re
from collections import Counter

root = r"C:\Hypernet\Hypernet Structure"
results = []

for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        fpath = os.path.join(dirpath, fn)
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()[:25]
            for line in lines:
                m = re.match(r'^ha:\s*["\']?([^"\'\r\n]+)["\']?\s*$', line)
                if m:
                    ha = m.group(1).strip()
                    rel = os.path.relpath(fpath, root)
                    results.append((ha, rel))
                    break
        except Exception:
            pass

ha_counts = Counter(ha for ha, _ in results)
dupes = {ha: count for ha, count in ha_counts.items() if count > 1}

print(f"Total files with ha: {len(results)}")
print(f"Unique addresses: {len(ha_counts)}")
print(f"Duplicate addresses: {len(dupes)}")
print()

for ha, count in sorted(dupes.items(), key=lambda x: (-x[1], x[0])):
    print(f"  {ha} ({count} files):")
    for h, p in results:
        if h == ha:
            print(f"    {p}")
    print()
