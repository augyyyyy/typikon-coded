import os

total = 0
results = []
for root, dirs, files in os.walk('engine'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            lines = len(open(path, encoding='utf-8').readlines())
            results.append((f, lines, path))
            total += lines

# Sort resolvers together
results.sort(key=lambda x: (0 if 'resolvers' not in x[2] else 1, x[0]))

print(f"Total lines: {total}")
print("| Module | Lines |")
print("|--------|------:|")
for f, l, p in results:
    # Get relative path/name
    rel = p.replace('engine\\', '').replace('\\', '/')
    print(f"| `{rel}` | {l} |")
