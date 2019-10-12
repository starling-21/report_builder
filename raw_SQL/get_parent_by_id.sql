SELECT u2.name, u1.name
FROM reports_unit u1
INNER JOIN reports_unit u2 
ON u1.id=u2.parent_unit_id
WHERE u2.id=2

SELECT u2.name, u1.name parent
FROM reports_unit u1
LEFT JOIN reports_unit u2 
ON u1.id=u2.parent_unit_id
WHERE u2.id=1