from sqlalchemy import Column, Integer, String, Float, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'customers'
    customerid = Column(Integer, primary_key=True)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    creditcard = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    balance = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    # Relación uno a muchos: Un usuario puede tener muchos pedidos
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan') #Para borrado en cascada

class Product(Base):
    __tablename__ = 'products'
    prod_id = Column(Integer, primary_key=True)
    movieid = Column(Integer, ForeignKey('imdb_movies.movieid'))
    price = Column(Numeric, nullable=False)
    description = Column(String(30), nullable=False)
    inventory = relationship("Inventory", back_populates="product") # Creamos una relación con la tabla inventory

class Inventory(Base):
    __tablename__ = 'inventory'
    prod_id = Column(Integer, ForeignKey('products.prod_id'), primary_key=True)
    stock = Column(Integer, nullable=False)
    sales = Column(Integer, nullable=False)
    product = relationship("Product", back_populates="inventory")

class Order(Base):
    __tablename__ = 'orders'
    orderid = Column(Integer, primary_key=True)
    orderdate = Column(Date)
    customerid = Column(Integer, ForeignKey('customers.customerid'))
    netamount = Column(Numeric)
    tax = Column(Numeric)
    totalamount = Column(Numeric)
    status = Column(String(10), nullable=False)
    
    # Relación inversa, los pedidos pertenecen a un usuario
    user = relationship('User', back_populates='orders') #Para borrado en cascada

class OrderDetail(Base):
    __tablename__ = 'orderdetail'
    orderid = Column(Integer, ForeignKey('orders.orderid'), primary_key=True)
    prod_id = Column(Integer, ForeignKey('inventory.prod_id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
