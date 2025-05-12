-- Añade columna 'balance' a la tabla 'customers' para el saldo del cliente
ALTER TABLE customers
ADD COLUMN balance NUMERIC(10, 2) DEFAULT 0;

-- Crea tabla 'ratings' para almacenar likes de los usuarios
CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES customers(customerid) ON DELETE CASCADE,
    product_id INT REFERENCES products(prod_id) ON DELETE CASCADE,
    is_liked BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (user_id, product_id)
);



-- Modifica la longitud del campo 'password' en la tabla 'customers'
ALTER TABLE customers
ALTER COLUMN password TYPE character varying(100);



-- Procedimiento para asignar saldo aleatorio entre 0 y N
CREATE OR REPLACE FUNCTION setCustomersBalance(IN initialBalance NUMERIC)
RETURNS VOID AS $$
BEGIN
    UPDATE customers
    SET balance = floor(random() * (initialBalance + 1))::NUMERIC;
END;
$$ LANGUAGE plpgsql;


-- Llamada al procedimiento con N = 200
SELECT setCustomersBalance(200);

\i actualizaPrecios.sql
\i actualizaTablas.sql
\i actualizaCarrito.sql
\i pagado.sql
\i actualizaPreciosPedidos.sql 
;
-- actualizaPreciosPedidos.sql: Archivo extra ( no solicitado en el enunciado ) ;)