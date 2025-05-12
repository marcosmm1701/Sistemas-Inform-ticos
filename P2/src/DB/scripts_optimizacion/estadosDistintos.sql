CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country);
CREATE INDEX IF NOT EXISTS idx_orders_orderdate_year ON orders(EXTRACT(YEAR FROM orderdate));

SELECT COUNT(DISTINCT state) AS estados_distintos
FROM customers c
JOIN orders o ON c.customerid = o.customerid
WHERE EXTRACT(YEAR FROM o.orderdate) = :anio
  AND c.country = :pais;