-- Eliminamos restricciones ON DELETE CASCADE
ALTER TABLE orders DROP CONSTRAINT IF EXISTS rel_orders_customers;
ALTER TABLE orderdetail DROP CONSTRAINT IF EXISTS rel_orderdetail_orders;

-- Añadimos restricciones sin ON DELETE CASCADE
ALTER TABLE orders 
    ADD CONSTRAINT rel_orders_customers 
    FOREIGN KEY (customerid) 
    REFERENCES customers (customerid);

ALTER TABLE orderdetail 
    ADD CONSTRAINT rel_orderdetail_orders 
    FOREIGN KEY (orderid) 
    REFERENCES orders (orderid);
