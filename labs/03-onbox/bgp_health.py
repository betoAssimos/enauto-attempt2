import cli

bgp_output = cli.execute("show ip bgp summary")

expected_neighbor = "172.31.1.4"
expected_as = "65100"

neighbor_found = False
neighbor_healthy = False

print("=== CISCO CORE BGP HEALTH CHECK ===")

for line in bgp_output.splitlines():

    # Extract local BGP information
    if line.startswith("BGP router identifier"):
        parts = line.split(",")
        router_id = parts[0].split()[-1]
        local_as = parts[1].split()[-1]

        print(f"Router ID: {router_id}")
        print(f"Local ASN: {local_as}")

    # Parse BGP neighbors
    fields = line.split()

    if not fields:
        continue

    if fields[0] == expected_neighbor:
        neighbor_found = True

        remote_as = fields[2]
        state = fields[-1]

        if remote_as == expected_as and state.isdigit():
            neighbor_healthy = True
            print(f"[PASS] BGP neighbor {expected_neighbor}")
            print(f"       Remote ASN: {remote_as}")
            print(f"       State: Established")
            print(f"       Prefixes received: {state}")
        else:
            print(f"[FAIL] BGP neighbor {expected_neighbor}")
            print(f"       Remote ASN: {remote_as}")
            print(f"       State/PfxRcd: {state}")

if not neighbor_found:
    print(f"[FAIL] BGP neighbor {expected_neighbor} not found")

if neighbor_healthy:
    print("OVERALL: PASS")
else:
    print("OVERALL: FAIL")