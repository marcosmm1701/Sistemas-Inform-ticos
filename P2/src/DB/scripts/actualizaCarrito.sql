
-- Paso 1: Crea la función que recalcule el total de un pedido
CREATE OR REPLACE FUNCTION actualiza_carrito_func()
RETURNS TRIGGER AS $$
BEGIN
    
    IF TG_OP = 'INSERT' THEN
        -- En un INSERT, siempre recalculamos el total
        PERFORM calcularTotalPedido(NEW.orderid);

    ELSIF TG_OP = 'UPDATE' THEN
        -- Solo recalculamos si las columnas 'price' o 'quantity' han cambiado
        IF NEW.price IS DISTINCT FROM OLD.price OR NEW.quantity IS DISTINCT FROM OLD.quantity THEN
            -- Recalculamos si los valores de price o quantity han cambiado
            PERFORM calcularTotalPedido(NEW.orderid);
        END IF;

    ELSIF TG_OP = 'DELETE' THEN
        -- En un DELETE, recalculamos los totales para el `orderid` del registro eliminado
        PERFORM calcularTotalPedido(OLD.orderid);
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


-- Paso 2: Crea el trigger que llame a la función después de cada operación en `orderdetail`
CREATE or REPLACE TRIGGER actualizaCarrito
AFTER INSERT OR UPDATE OR DELETE ON orderdetail
FOR EACH ROW
EXECUTE FUNCTION actualiza_carrito_func();
