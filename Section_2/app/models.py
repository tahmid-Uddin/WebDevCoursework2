from app import db
from flask_login import UserMixin

# Many-Many relationship: user - listing through wishlist association table
# One-Many relationship: listing->cart, listing->images user->listing
# One-One relationsihp: user->cart

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
    address = db.Column(db.String(200), nullable=True)
    password_hash = db.Column(db.String(128))
    is_seller = db.Column(db.Boolean, nullable=False)
    
    
class Listing(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False) 
    image = db.relationship('Image', backref='image', lazy='dynamic')
    cart = db.relationship('Cart', backref='cart', lazy='dynamic')


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('listing.product_id'), nullable=False)


class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('listing.product_id'), nullable=False)
    id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

