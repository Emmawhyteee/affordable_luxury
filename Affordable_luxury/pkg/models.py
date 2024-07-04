from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class State(db.Model):
    state_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    state_name = db.Column(db.String(100),nullable=False) 
    state_lgaid = db.Column(db.Integer,db.ForeignKey('lga.lga_id'))
    #set relationship
    state_lga = db.relationship('Lga', back_populates ='lga_state')
    state_cust = db.relationship('Customer', back_populates ='cust_state')
   
class Lga(db.Model):
    lga_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    lga_name = db.Column(db.String(100),nullable=False)   
    lga_state = db.relationship('State', back_populates ='state_lga')
    lga_cust = db.relationship('Customer', back_populates ='cust_lga')

   
      
class Customer(db.Model):  
    cust_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    cust_fname = db.Column(db.String(100), nullable=False)
    cust_lname = db.Column(db.String(100), nullable=False)
    cust_email = db.Column(db.String(120), nullable=False,unique=True) 
    cust_address = db.Column(db.String(120), nullable=True) 
    cust_password=db.Column(db.String(255), nullable=True)
    cust_phone=db.Column(db.String(120), nullable=True) 
    cust_pix=db.Column(db.String(255), nullable=True) 
    #set the foreign key 
    cust_lgaid=db.Column(db.Integer, db.ForeignKey('lga.lga_id'))
    cust_stateid=db.Column(db.Integer, db.ForeignKey('state.state_id')) 
    #set relationships
    cust_lga=db.relationship('Lga', back_populates ='lga_cust')
    cust_state=db.relationship('State', back_populates='state_cust') 
    cust_payment=db.relationship('Payment', back_populates='payment_cust') 


    
   
class Category(db.Model):
    cat_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    cat_name = db.Column(db.String(100),nullable=False)
    cat_prod = db.relationship('Product', back_populates ='prod_cat')

   
    
class Product(db.Model):
    prod_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    prod_description= db.Column(db.String(225),nullable=False)
    prod_title= db.Column(db.String(100),nullable=False)
    prod_price= db.Column(db.String(100),nullable=False)
    # prod_quantity= db.Column(db.String(100),nullable=False)
    prod_availability= db.Column(db.Enum('Available','Out of Stock'),server_default='Available') # prod_availability=db.Column(db.Enum('pending','Available','Not'), nullable=False)
    prod_cat = db.relationship('Category', back_populates ='cat_prod')
    prod_catid= db.Column(db.Integer,db.ForeignKey('category.cat_id'))

    prod_date= db.Column(db.DateTime, default=datetime.utcnow)
    prod_image= db.Column(db.String(255),nullable=False)#what data type is for storing images


   #...................................CART START..................................................................

   #.....................................CART END................................................................
class Prod_order(db.Model):
    prod_orderid = db.Column(db.Integer, autoincrement=True,primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey('order.order_id'))
    prod_id = db.Column(db.Integer,db.ForeignKey('product.prod_id'))
    quantity = db.Column(db.Integer,nullable=False)
   
    
class Order(db.Model):
    order_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    order_custid = db.Column(db.Integer,db.ForeignKey('customer.cust_id'))
    order_date = db.Column(db.DateTime,default=datetime.utcnow)
    total_amount = db.Column(db.Integer,nullable=False)
    order_status = db.Column(db.String(100),nullable=False)
   
    
    
class Payment(db.Model):
    payment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    payment_orderid = db.Column(db.Integer,db.ForeignKey('order.order_id'))
    amount_paid = db.Column(db.Integer,nullable=False)
    payment_custid = db.Column(db.Integer,db.ForeignKey('customer.cust_id'))
    transaction_details = db.Column(db.String(100),nullable=False)
    payment_date = db.Column(db.DateTime,default=datetime.utcnow)
    payment_status = db.Column(db.Enum('pending','paid','failed'),nullable=False)
    payment_ref = db.Column(db.String(100),nullable=False)
    payment_cust=db.relationship('Customer', back_populates='cust_payment') 
    
    
class Admin(db.Model):
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_pwd=db.Column(db.String(255),nullable=True)
    admin_email=db.Column(db.String(120),nullable=False)
    last_loggedin=db.Column(db.DateTime,default=datetime.utcnow)

