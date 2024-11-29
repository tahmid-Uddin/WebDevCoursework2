from flask import render_template, flash, request, redirect, url_for
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from .models import User, Listing, Image, Cart
from .forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Listing, db.session))
admin.add_view(ModelView(Image, db.session))
admin.add_view(ModelView(Cart, db.session))

@app.route('/')
def home():
    products = [
    {"name": "Dog Collar", "price": 10.99, "in_stock": True, "image": "images/dog_collar.jpg"},
    {"name": "Cat Toy", "price": 5.49, "in_stock": False, "image": "images/cat_toy.jpg"},
    {"name": "Bird Cage", "price": 50.00, "in_stock": True, "image": "images/bird_cage.jpg"}
    ]
    return render_template('adoption.html', products=products, user=current_user)


@app.route('/accessories', methods=['GET', 'POST'])
def accessories():
    return render_template('accessories.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():  # Check if form was submitted and is valid
        enteredEmail = form.email.data
        enteredPassword = form.password.data
        user = User.query.filter_by(email=enteredEmail).first()
        
        if user and check_password_hash(user.password_hash, enteredPassword):
            login_user(user, remember=True)
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.")
    
    return render_template('login.html', form=form, user=current_user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        if form.password.data != request.form.get("passwordConfirmation"):
            flash("Passwords do not match.")
            return redirect('/signup')
        
        if User.query.filter_by(email=form.email.data).first():
            flash("An account with the email already exists.")
            return redirect('/signup')
               
        name = form.firstName.data.split(" ")
        if len(name) == 1: middleName = None 
        else: middleName = " ".join([x.capitalize() for x in name[1:]])
            
        user = User(first_name = name[0].capitalize(), 
                    middle_name = middleName, 
                    last_name = form.lastName.data.capitalize(),
                    email = form.email.data,
                    password_hash = generate_password_hash(form.password.data),
                    is_seller = False)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        return redirect(url_for("home")) 
    
    return render_template('sign_up.html', form=form, user=current_user)



