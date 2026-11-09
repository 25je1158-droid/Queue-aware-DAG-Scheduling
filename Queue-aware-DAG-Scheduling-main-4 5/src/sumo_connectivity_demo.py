from sumo_loader import load_trace

trace = load_trace()

print("Total Records:")
print(len(trace))

print()

print("Unique Vehicles:")
print(trace["vehicle"].nunique())

print()

print("Columns:")
print(trace.columns)

print()

print("First 5 Records:")
print(trace.head())
