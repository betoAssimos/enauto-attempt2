from jinja2 import Template, FileSystemLoader, Environment

interfaces = [
    {"name": "GigabitEthernet1", "ip": "10.0.0.1", "mask": "255.255.255.0", "desc": "uplink"},
    {"name": "GigabitEthernet2", "ip": "10.0.1.1", "mask": "255.255.255.0", "desc": "access"},
    {"name": "GigabitEthernet3", "ip": "10.0.2.1", "mask": "255.255.255.0", "desc": "mgmt"},
]

t =Template("interface {{ name }}")
print(type(t))
out = t.render(name="Gi2")
print(type(out))
print(out)
