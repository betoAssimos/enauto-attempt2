# A minimal IOS XE ZTP Python script fetched via DHCP option 67.
# It runs inside the device's Guest Shell at first boot.
from cli import configure # 'cli' module is provided on-box
day0 = """
hostname BRANCH-SW01
!
username automation privilege 15 secret Cisco123!
!
interface GigabitEthernet0/0
ip address dhcp
no shutdown
!
netconf-yang
restconf
ip http secure-server
"""
print("Applying Day-0 configuration...")
configure(day0.splitlines()) # push each line into running-config
print("Day-0 complete; device is now manageable via NETCONF/RESTCONF.")

