from jinja2 import Template, FileSystemLoader, Environment

interfaces = [
    {"name": "GigabitEthernet1", "ip": "10.0.0.1", "mask": "255.255.255.0", "desc": "uplink"},
    {"name": "GigabitEthernet2", "ip": "10.0.1.1", "mask": "255.255.255.0", "desc": "access"},
    {"name": "GigabitEthernet3", "ip": "10.0.2.1", "mask": "255.255.255.0", "desc": "mgmt"},
]

t = Template("""{% for intf in interfaces %}
interface {{ intf.name }}
 description {{ intf.desc }}
{% endfor %}""")
out = t.render(interfaces=interfaces)
print(repr(out))
print("-----------------------------------------------------")
TPL = """{% for intf in interfaces %}
interface {{ intf.name }}
 description {{ intf.desc }}
{% endfor %}"""
print(repr(Environment().from_string(TPL).render(interfaces=interfaces)))
print(repr(Environment(trim_blocks=True, lstrip_blocks=True).from_string(TPL).render(interfaces=interfaces)))
