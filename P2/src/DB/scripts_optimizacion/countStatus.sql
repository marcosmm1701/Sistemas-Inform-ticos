-- Consultas iniciales sobre base de datos sin índices ni estadísticas
EXPLAIN SELECT count(*) FROM orders WHERE status IS NULL;
EXPLAIN SELECT count(*) FROM orders WHERE status = 'Shipped';

-- Crear un índice en la columna status de la tabla orders
CREATE INDEX idx_orders_status ON orders(status);

-- Consultas después de crear el índice, pero sin estadísticas
EXPLAIN SELECT count(*) FROM orders WHERE status IS NULL;
EXPLAIN SELECT count(*) FROM orders WHERE status = 'Shipped';

-- Generar estadísticas de la tabla orders
ANALYZE orders;

-- Consultas después de generar las estadísticas
EXPLAIN SELECT count(*) FROM orders WHERE status IS NULL;
EXPLAIN SELECT count(*) FROM orders WHERE status = 'Shipped';

-- Consultas adicionales para comparar después de tener índice y estadísticas
EXPLAIN SELECT count(*) FROM orders WHERE status = 'Paid';
EXPLAIN SELECT count(*) FROM orders WHERE status = 'Processed';