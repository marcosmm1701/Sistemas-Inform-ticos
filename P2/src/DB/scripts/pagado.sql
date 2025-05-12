-- Actualiza el inventario y el saldo del cliente cuando un pedido cambia a estado "Paid".
CREATE OR REPLACE FUNCTION pedido_pagado()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica que el nuevo estado es "Paid"
    IF NEW.status = 'Paid' THEN
        -- Actualiza inventario: descuenta la cantidad de cada producto en el pedido usando un solo UPDATE
        UPDATE inventory
        SET stock = stock - od.quantity, sales = sales + od.quantity
        FROM orderdetail od
        WHERE od.orderid = NEW.orderid AND inventory.prod_id = od.prod_id;
          

        -- Descuenta el saldo del cliente en función del total del pedido
        UPDATE customers
        SET balance = balance - NEW.totalamount
        WHERE customerid = NEW.customerid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Crea el trigger para actualizar el inventario y el saldo del cliente
CREATE or REPLACE TRIGGER pagado
AFTER UPDATE OF status ON orders
FOR EACH ROW
WHEN (NEW.status = 'Paid')
EXECUTE FUNCTION pedido_pagado();
