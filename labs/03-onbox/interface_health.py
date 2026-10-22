import cli
output = cli.execute("show ip interface brief")

results = []

target_interfaces = ["GigabitEthernet3", "GigabitEthernet4"]

interfaces = output.splitlines()
for interface in interfaces:
  fields = interface.split()
  if not fields:
    continue
  if fields[0] in target_interfaces:
   if fields[-1] == "up" and fields[-2] == "up":
    results.append(fields[0])
for name in target_interfaces:
 if name in results:
  print(f"[PASS] {name}")
 else:
  print(f"[FAIL] {name}")
if len(results) == len(target_interfaces):
 print("OVERALL: PASS")
else:
 print("OVERALL: FAIL")