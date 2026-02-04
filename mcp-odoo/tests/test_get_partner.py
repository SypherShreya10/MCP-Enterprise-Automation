from tools.crm import get_partner

print(get_partner(email="contact@autocorp.com"))
print(get_partner(name="AutoCorp", limit=5))
print(get_partner(is_customer=True, name="%", limit=10))
print(get_partner(name="MCP Test Partner"))
