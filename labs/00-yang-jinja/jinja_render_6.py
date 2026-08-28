from jinja2 import Template, FileSystemLoader, Environment

interfaces = [
    {"name": "GigabitEthernet1", "ip": "10.0.0.1", "mask": "255.255.255.0", "desc": "uplink"},
    {"name": "GigabitEthernet2", "ip": "10.0.1.1", "mask": "255.255.255.0", "desc": "access"},
    {"name": "GigabitEthernet3", "ip": "10.0.2.1", "mask": "255.255.255.0", "desc": "mgmt"},
]

env = Environment(loader=FileSystemLoader("labs/00-yang-jinja/templates/"))
template = env.get_template("interfaces_1.j2")
output = template.render(interfaces=interfaces)
print(output)
