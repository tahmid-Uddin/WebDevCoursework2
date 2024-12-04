from app import db
import datetime
from flask_login import UserMixin

#Association table for user and product, many to many relationship
wishlist_table = db.Table(
    "wishlist_table",
    db.Model.metadata,
    db.Column("id", db.ForeignKey("user.id")),
    db.Column("product_id", db.ForeignKey("listing.product_id")),
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(300), nullable=True)
    post_code = db.Column(db.String(10), nullable=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    
    seller = db.relationship("Seller", backref="user", uselist=False)
    cart = db.relationship("Cart", backref="user", uselist=False)
    orders = db.relationship("Orders", backref="user", lazy="dynamic")
    
    
class Seller(db.Model):   
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    
    business_name = db.Column(db.String(100), nullable=False)
    business_phone = db.Column(db.String(20), nullable=False)
    business_email = db.Column(db.String(120), nullable=False)
    business_address = db.Column(db.String(300), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    
    listings = db.relationship("Listing", backref="seller", lazy="dynamic")  # plural since one-to-many
    orders = db.relationship("Orders", backref="seller", lazy="dynamic")
    
    
class Listing(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("seller.id"), nullable=False) 
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    
    images = db.relationship("Image", backref="image", lazy="dynamic") 
    cart = db.relationship("Cart", backref="cart", lazy="dynamic")


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("listing.product_id"), nullable=False)
    img = db.Column(db.LargeBinary, unique=True, nullable=False)
    filename = db.Column(db.String(50), nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    


class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("listing.product_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    
class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("seller.id"), nullable=False)
    
    product_name = db.Column(db.String(500), nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    quantity = db.Column(db.Integer, nullable=False)
    order_time = db.Column(db.DateTime, nullable=False)

