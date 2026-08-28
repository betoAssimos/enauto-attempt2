from jinja2 import Template, FileSystemLoader, Environment

interfaces = [
    {"name": "GigabitEthernet1", "ip": "10.0.0.1", "mask": "255.255.255.0", "desc": "uplink"},
    {"name": "GigabitEthernet2", "ip": "10.0.1.1", "mask": "255.255.255.0", "desc": "access"},
    {"name": "GigabitEthernet3", "ip": "10.0.2.1", "mask": "255.255.255.0", "desc": "mgmt"},
]

t =Template("{%for intf in interfaces %} {{loop.index}}\n{%endfor%}")
out1 = t.render(interfaces=interfaces)
print("loop index:", out1)

t =Template("{%for intf in interfaces %} {{loop.index0}}\n{%endfor%}")
out2 = t.render(interfaces=interfaces)
print("loop index 0-based:", out2)

t =Template("{%for intf in interfaces %} {{loop.first}}\n{%endfor%}")
out3 = t.render(interfaces=interfaces)
print("loop first:", out3)

t =Template("{%for intf in interfaces %} {{loop.last}}\n{%endfor%}")
out4 = t.render(interfaces=interfaces)
print("loop last:", out4)

t =Template("{%for intf in interfaces %} {{loop.length}}\n{%endfor%}")
out5 = t.render(interfaces=interfaces)
print("loop length:", out5)

t = Template("{% for intf in interfaces %}! interface {{ loop.index }} of {{ loop.length }}\ninterface {{ intf.name }}\n{% endfor %}")
out6 = t.render(interfaces=interfaces)
print("loop index:\n", out6)