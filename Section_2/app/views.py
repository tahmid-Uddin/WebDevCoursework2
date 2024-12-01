from flask import render_template, flash, request, redirect, url_for
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from .models import User, Listing, Image, Cart, Seller
from .forms import SignUpForm, LoginForm, UpdateUserForm, SellerRegistrationForm, CreateListingForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Listing, db.session))
admin.add_view(ModelView(Image, db.session))
admin.add_view(ModelView(Cart, db.session))
admin.add_view(ModelView(Seller, db.session))

@app.route('/')
def home():
    products = [
    {"name": "Dog", "price": 10.99, "in_stock": True, "image": "images/dog_collar.jpg"},]
    return render_template('adoption.html', products=products, user=current_user)


@app.route('/accessories', methods=['GET', 'POST'])
def accessories():
    products = [
    {"name": "Dog Collar", "price": 10.99, "in_stock": True, "image": "images/dog_collar.jpg"},
    {"name": "Cat Toy", "price": 5.49, "in_stock": False, "image": "images/cat_toy.jpg"},
    {"name": "Bird Cage", "price": 50.00, "in_stock": True, "image": "images/bird_cage.jpg"}
    ]
    return render_template('accessories.html', products=products, user=current_user)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    updateUserForm = UpdateUserForm()
    sellerForm = SellerRegistrationForm()
    seller = Seller.query.get(current_user.id)
    user = User.query.get(current_user.id)
    
    if updateUserForm.validate_on_submit():
        user.first_name = updateUserForm.firstName.data
        user.middle_name = updateUserForm.middleName.data
        user.last_name = updateUserForm.lastName.data
        
        if updateUserForm.phoneNumber.data and updateUserForm.phoneNumber.data.strip():
            user.phone_number = updateUserForm.phoneNumber.data
            
        if updateUserForm.address.data and updateUserForm.address.data.strip():
            user.address = updateUserForm.address.data
            
        db.session.commit()
        flash("Details updated Successfully")
        return redirect(url_for("account"))
        
    if request.method == 'GET':
        updateUserForm.firstName.data = user.first_name
        updateUserForm.middleName.data = user.middle_name
        updateUserForm.lastName.data = user.last_name
        updateUserForm.phoneNumber.data = user.phone_number
        updateUserForm.address.data = user.address
        
    return render_template('account.html', form=updateUserForm, sellerForm=sellerForm, user=current_user, seller=seller)


@app.route('/seller', methods=['GET', 'POST'])
@login_required
def seller():
    sellerForm = SellerRegistrationForm()
    listingForm = CreateListingForm()
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    user = User.query.get(current_user.id)

    if 'submitBusinessDetails' in request.form:
        if sellerForm.validate_on_submit():
            if seller:
                seller.business_name = sellerForm.businessName.data
                seller.business_phone = sellerForm.businessPhone.data
                seller.business_address = sellerForm.businessAddress.data
                seller.country = sellerForm.country.data
            else:
                new_seller = Seller(business_name=sellerForm.businessName.data,
                                    business_phone=sellerForm.businessPhone.data,
                                    business_address=sellerForm.businessAddress.data,
                                    country=sellerForm.country.data,
                                    user_id=current_user.id)
                
                db.session.add(new_seller)
                
            db.session.commit()
            flash("Business details updated successfully", category="success")
            return redirect(url_for("seller"))
        
        else:
            flash("Error updating business details", category="error")
        

    if 'submitNewListing' in request.form:
        if listingForm.validate_on_submit():
            new_listing = Listing(seller_id=seller.id,
                                  name=listingForm.name.data,
                                  description=listingForm.description.data,
                                  stock=listingForm.stock.data,
                                  price=listingForm.price.data,
                                  category=listingForm.category.data)
            
            db.session.add(new_listing)
            db.session.commit()

            if request.files.getlist('image'):
                upload_dir = os.path.join('app', 'static', 'product_images')
                
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                for file in request.files.getlist('image'):
                    if file:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(upload_dir, filename)
                        file.save(file_path)
                        
                        try:
                            new_image = Image(product_id=new_listing.product_id,
                                            url=os.path.join('product_images', filename))
                            db.session.add(new_image)
                        except:
                            flash("Error creating new listing: failed image upload.", category="error")

            
            db.session.commit()
            flash("New listing created successfully.", category="success")
            return redirect(url_for("seller"))

        else:
            flash("Error creating new listing: invalid product information.", category="error")

    # Prepare existing listings for display
    existing_listings = []
    if seller:
        existing_listings = Listing.query.filter_by(seller_id=seller.id).all()

    # Prepopulate forms if seller exists
    if seller:
        sellerForm.businessName.data = seller.business_name
        sellerForm.businessPhone.data = seller.business_phone
        sellerForm.businessAddress.data = seller.business_address
        sellerForm.country.data = seller.country

    return render_template('seller.html', sellerForm=sellerForm, listingForm=listingForm, user=user, seller=seller, listings=existing_listings)

@app.route('/delete_listing/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    
    if not seller or listing.seller_id != seller.id:
        flash("You are not authorized to delete this listing", category="error")
        return redirect(url_for("seller"))
    
    Image.query.filter_by(product_id=listing.product_id).delete()
    db.session.delete(listing)
    db.session.commit()
    
    flash("Listing deleted successfully", category="success")
    return redirect(url_for("seller"))

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
                    password_hash = generate_password_hash(form.password.data))
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        return redirect(url_for("home")) 
    
    return render_template('sign_up.html', form=form, user=current_user)



