from tools.crm import create_partner

result = create_partner(
    name="MCP Test Partner 2",
    email="mcp.test.partner2@example.com",
    phone="+1-555-000-0001",
    is_customer=True,
)

print(result)
