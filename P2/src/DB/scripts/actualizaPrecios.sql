
CREATE INDEX idx_orderdetail_orderid ON orderdetail(orderid);
CREATE INDEX idx_orderdetail_prod_id ON orderdetail(prod_id);
CREATE INDEX idx_orders_orderid ON orders(orderid);


-- Función para calcular el total de un pedido específico
CREATE OR REPLACE FUNCTION calcularTotalPedido(order_id INT)
RETURNS VOID AS $$
BEGIN
    -- 1. Actualiza el campo price en orderdetail con el precio del producto desde products
    UPDATE orderdetail od
    SET price = p.price
    FROM products p
    WHERE od.prod_id = p.prod_id AND od.orderid = order_id;

    -- 2. Calcula el subtotal neto y actualizar netamount en orders
    UPDATE orders
    SET netamount = (
        SELECT SUM(od.price * od.quantity)
        FROM orderdetail od
        WHERE od.orderid = orders.orderid
    )
    WHERE orderid = order_id;

    -- 3. Calcula el total con impuestos y actualizar totalamount en orders
    UPDATE orders
    SET totalamount = netamount + (netamount * tax / 100)
    WHERE orderid = order_id;
END;
$$ LANGUAGE plpgsql;


-- Función para actualizar todos los pedidos en bloques de 500
CREATE OR REPLACE FUNCTION actualizarTodosLosPedidos()
RETURNS VOID AS $$
DECLARE
    pedidos CURSOR FOR SELECT orderid FROM orders;
    pedido_id INT;
    contador INT := 0;
BEGIN
    OPEN pedidos;
    LOOP
        FETCH pedidos INTO pedido_id;
        EXIT WHEN NOT FOUND;
        
        -- Llama a calcularTotalPedido para el pedido actual
        PERFORM calcularTotalPedido(pedido_id);
        
        -- Incrementa el contador y verificar si ha llegado a 500
        contador := contador + 1;
        IF contador >= 10000 THEN
            contador := 0;
            -- Hace una pausa breve para evitar la sobrecarga
            PERFORM pg_sleep(0.2); -- pausa de 0.2 segundos, opcional
        END IF;
    END LOOP;
    CLOSE pedidos;
END;
$$ LANGUAGE plpgsql;



-- Llama a la función para actualizar todos los pedidos
SELECT actualizarTodosLosPedidos();