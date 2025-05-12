-- Archivo extra ( no solicitado en el enunciado )
-- Descripción: Script que crea un trigger que actualiza los precios de los productos en los pedidos cuando se modifica el precio de un producto.

CREATE OR REPLACE FUNCTION actualizar_precios_pedidos()
RETURNS TRIGGER AS $$
DECLARE
    order_rec RECORD;
BEGIN
    -- Primero, actualizamos el precio en `orderdetail` para todos los pedidos que contienen el producto modificado
    UPDATE orderdetail
    SET price = NEW.price
    WHERE prod_id = NEW.prod_id;

    -- Luego, recalculamos el total de cada pedido afectado
    FOR order_rec IN
        SELECT DISTINCT orderid
        FROM orderdetail
        WHERE prod_id = NEW.prod_id
    LOOP
        -- Recalcula el total para cada pedido
        PERFORM calcularTotalPedido(order_rec.orderid);
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


-- Crea el trigger para actualizar los precios en los pedidos
CREATE or REPLACE TRIGGER actualizarPreciosPedidos
AFTER UPDATE OF price ON products
FOR EACH ROW
EXECUTE FUNCTION actualizar_precios_pedidos();
