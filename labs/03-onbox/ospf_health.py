import cli
ospf_output = cli.execute("show ip ospf neighbor")
print(ospf_output)
routerID = "10.200.99"
intf = "GigabitEthernet4"
neighbor_found = False
result = ospf_output.splitlines()
for line in result:
 fields = line.split()
 if not fields:
  continue
 if fields[0] == routerID:
  neighbor_found = True
  if fields[2].startswith("FULL") and fields[-1] == intf:
   print(f"[PASS] OSPF neighbor {fields[0]} is {fields[2]} on {fields[-1]}")
  else:
   print(f"[FAIL] OSPF neighbor {fields[0]} is {fields[2]} on {fields[-1]}")
if not neighbor_found:
  print(f"[FAIL] OSPF neighbor {routerID} not found")