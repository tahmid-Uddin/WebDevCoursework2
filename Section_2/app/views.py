from flask import render_template
from app import app

@app.route('/')
def index():
    products = [
    {"name": "Dog Collar", "price": 10.99, "in_stock": True, "image": "images/dog_collar.jpg"},
    {"name": "Cat Toy", "price": 5.49, "in_stock": False, "image": "images/cat_toy.jpg"},
    {"name": "Bird Cage", "price": 50.00, "in_stock": True, "image": "images/bird_cage.jpg"}
    ]
    return render_template('home.html', products=products)

@app.route('/accessories', methods=['GET', 'POST'])
def accessories():
    
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    return render_template('home.html')

