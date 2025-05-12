-- Añadimos la columna 'promo' para descuentos en clientes
ALTER TABLE customers ADD COLUMN promo DECIMAL(5, 2) DEFAULT 0;


-- Función para actualizar los precios en el carrito del cliente con el descuento
CREATE OR REPLACE FUNCTION update_cart_price() RETURNS TRIGGER AS $$
BEGIN
    -- Pausa de 5 segundos durante la ejecución del trigger
    PERFORM pg_sleep(10);

    -- Actualizamos el precio de los pedidos basándonos en el valor de la columna 'promo'
    UPDATE orders
    SET netamount = netamount * (1 - NEW.promo / 100)
    WHERE orderid IN (SELECT orderid FROM orders WHERE customerid = NEW.customerid);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creamos el trigger que se activará después de actualizar 'promo'
CREATE TRIGGER after_promo_update
AFTER UPDATE OF promo ON customers
FOR EACH ROW
EXECUTE FUNCTION update_cart_price();