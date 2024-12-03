from flask import render_template, flash, request, redirect, url_for
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from .models import User, Listing, Image, Cart, Seller, wishlist_table, Orders
from .forms import SignUpForm, LoginForm, UpdateUserForm, SellerRegistrationForm, CreateListingForm, ConfirmDeliveryDetailsForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
import datetime


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Listing, db.session))
admin.add_view(ModelView(Image, db.session))
admin.add_view(ModelView(Cart, db.session))
admin.add_view(ModelView(Seller, db.session))
admin.add_view(ModelView(Orders, db.session))

@app.route("/")
def home():
    return redirect(url_for("adoption"))

def get_products(category):
    listings = Listing.query.filter_by(category=category).all()
    products = []
    for listing in listings:
        product = {
            "product_id": listing.product_id,
            "name": listing.name,
            "price": listing.price,
            "in_stock": listing.stock > 0,
            "images": []
        }
        
        images = Image.query.filter_by(product_id=listing.product_id).all()
        for image in images:
            product["images"].append(image.url)
            
        products.append(product)
    
    return products

@app.route("/adoption")
def adoption():
    products = get_products("adoption")
    
    return render_template("view_products.html", products=products, user=current_user)


@app.route("/accessories", methods=["GET", "POST"])
def accessories():
    products = get_products("accessory")
    
    return render_template("view_products.html", products=products, user=current_user)


@app.route("/adoption/<int:listing_id>", methods=["POST", "GET"])
@app.route("/accesory/<int:listing_id>", methods=["POST", "GET"])
def listingPage(listing_id):
    listing = Listing.query.filter_by(product_id=listing_id).first()
    seller = Seller.query.filter_by(id=listing.seller_id).first()
    product = {"product_id": listing.product_id,
               "name": listing.name,
               "description": listing.description,
               "price": listing.price,
               "in_stock": listing.stock > 0,
               "quantity": listing.stock,
               "images": []}
    
    images = Image.query.filter_by(product_id=listing.product_id).all()
    for image in images:
        product["images"].append(image.url)
            
    if "addToWishlist" in request.form:
        addToWishlist = wishlist_table.insert().values(id=current_user.id, product_id=listing_id)
        db.session.execute(addToWishlist)
        db.session.commit()


    return render_template("listing_page.html", product=product, seller=seller, user=current_user, image_count=len(product["images"]))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    itemsInCart = Cart.query.filter_by(user_id=current_user.id).all()
    if itemsInCart:
        products = []
        for item in itemsInCart:
            listing = Listing.query.filter_by(product_id=item.product_id).first()
            product = {
                    "cart_id": item.cart_id,
                    "name": listing.name,
                    "price": listing.price,
                    "description": listing.description,
                    "in_stock": listing.stock > 0,
                    "quantity": item.quantity,
                    "total_price": item.quantity * listing.price,
                    "image": None}
            image = Image.query.filter_by(product_id=listing.product_id).first()
            product["image"] = (image.url)
            
            products.append(product)
        
        total_price = sum([product["total_price"] for product in products if product["in_stock"]])
        total_quantity = sum([product["quantity"] for product in products if product["in_stock"]])
    
    else:
        products, total_price, total_quantity = None, None, None
            
    return render_template("cart.html", products=products, user=current_user, total_price=total_price, total_quantity=total_quantity)


@app.route("/add_to_cart/<int:listing_id>", methods=["POST"])
@login_required
def addToCart(listing_id):
    listing = Listing.query.filter_by(product_id=listing_id).first()
    itemAlreadyInCart = Cart.query.filter_by(user_id=current_user.id, product_id=listing_id).first()        
    if itemAlreadyInCart:
        newQuantity = itemAlreadyInCart.quantity + int(request.form.get("quantity", 1))
        if ((itemAlreadyInCart.quantity == listing.stock) or 
            (newQuantity > listing.stock)):
            flash("Item already in cart. Not enough in stock to add more.", category="error")
        
        else:
            itemAlreadyInCart.quantity += int(request.form.get("quantity", 1))
            db.session.commit()
            flash("Item(s) added to cart.", category="success")
        
    else:
        itemToCart = Cart(user_id=current_user.id,
                        product_id=listing_id,
                        quantity=int(request.form.get("quantity", 1)))
        db.session.add(itemToCart)
        db.session.commit()
        
    return redirect(url_for("listingPage", listing_id=listing_id))


@app.route("/deleteFromCart/<int:cart_id>", methods=["POST"])
@login_required
def deleteFromCart(cart_id):
    Cart.query.filter_by(cart_id=cart_id).delete()
    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    user = User.query.filter_by(id=current_user.id).first()
    confirmDeliveryDetails = ConfirmDeliveryDetailsForm()
    
    if "submitDeliveryDetails" in request.form:
        if confirmDeliveryDetails.validate_on_submit():
            user.first_name = confirmDeliveryDetails.firstName.data.strip()
            user.middle_name = confirmDeliveryDetails.middleName.data.strip()
            user.last_name = confirmDeliveryDetails.lastName.data.strip()
            user.phone_number = confirmDeliveryDetails.phoneNumber.data.strip()
            user.address = confirmDeliveryDetails.address.data.strip()
            user.post_code = confirmDeliveryDetails.postCode.data.strip()
                
            db.session.commit()
            
            datetime.datetime.now()
            cart = Cart.query.filter_by(user_id=current_user.id).all()
            order_time = datetime.datetime.now()
            for item in cart:
                product = Listing.query.filter_by(product_id=item.product_id).first()
                order = Orders(user_id=current_user.id,
                               product_id=item.product_id,
                               seller_id=product.seller_id,
                               quantity=item.quantity,
                               order_time=order_time)
                db.session.add(order)
                
                listing = Listing.query.filter_by(product_id=item.product_id).first()
                listing.stock -= item.quantity
                
                Cart.query.filter_by(cart_id=item.cart_id).delete()
                
                db.session.commit()
                
            flash("Successfully Placed Order", category="success")
            return redirect(url_for("pastOrders"))

    if request.method == "GET":
        confirmDeliveryDetails.firstName.data = user.first_name
        confirmDeliveryDetails.middleName.data = user.middle_name
        confirmDeliveryDetails.lastName.data = user.last_name
        confirmDeliveryDetails.phoneNumber.data = user.phone_number
        confirmDeliveryDetails.address.data = user.address
        confirmDeliveryDetails.postCode.data = user.post_code
        
    
    
    return render_template("checkout.html", form=confirmDeliveryDetails, user=current_user)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    updateUserForm = UpdateUserForm()
    sellerForm = SellerRegistrationForm()
    seller = Seller.query.get(current_user.id)
    user = User.query.get(current_user.id)
    
    if updateUserForm.validate_on_submit():
        user.first_name = updateUserForm.firstName.data.strip()
        user.middle_name = updateUserForm.middleName.data.strip()
        user.last_name = updateUserForm.lastName.data.strip()
        user.phone_number = updateUserForm.phoneNumber.data.strip()
        user.address = updateUserForm.address.data.strip()
        user.post_code = updateUserForm.postCode.data.strip()
            
        db.session.commit()
        flash("Details updated Successfully", category="success")
        return redirect(url_for("account"))
        
    if request.method == "GET":
        updateUserForm.firstName.data = user.first_name
        updateUserForm.middleName.data = user.middle_name
        updateUserForm.lastName.data = user.last_name
        updateUserForm.phoneNumber.data = user.phone_number
        updateUserForm.address.data = user.address
        updateUserForm.postCode.data = user.post_code
        
    return render_template("account.html", form=updateUserForm, sellerForm=sellerForm, user=current_user, seller=seller)


@app.route("/past_orders", methods=["GET", "POST"])
@login_required
def pastOrders():
    userOrders = Orders.query.filter_by(user_id=current_user.id).all()
    pastOrders = []
    
    orderIdentifier = []
    for order in userOrders:
        if order.order_time not in orderIdentifier:
            orderIdentifier.append(order.order_time)
            
    orderIdentifier = reversed(sorted(orderIdentifier))
            
    for identifier in orderIdentifier:
        orderGroup = Orders.query.filter_by(user_id=current_user.id, order_time=identifier).all()
        productsInOrder = []
        for index, order in enumerate(orderGroup):
            listing = Listing.query.filter_by(product_id=order.product_id).first()
            product = {
                    "name": listing.name,
                    "price": listing.price,
                    "description": listing.description,
                    "quantity": order.quantity,
                    "total_price": order.quantity * listing.price,
                    "image": None,
                    "order_ref": None}
            image = Image.query.filter_by(product_id=listing.product_id).first()
            product["image"] = (image.url)
            
            if index == 0:
                product["order_ref"] = "".join([x for x in str(order.order_time) if x.isdigit()])
            
            productsInOrder.append(product)
            
        #total_price = sum([product["total_price"] for product in productsInOrder])
        #productsInOrder.append(total_price)
        pastOrders.append(productsInOrder)

    return render_template("past_orders.html", pastOrders=pastOrders, user=current_user)


@app.route("/seller", methods=["GET", "POST"])
@login_required
def seller():
    sellerForm = SellerRegistrationForm()
    listingForm = CreateListingForm()
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    user = User.query.get(current_user.id)
    
    if "submitSellerRegistration" in request.form:
        if sellerForm.validate_on_submit():
            new_seller = Seller(business_name=sellerForm.businessName.data,
                                business_email=sellerForm.businessEmail.data,
                                business_phone=sellerForm.businessPhone.data,
                                business_address=sellerForm.businessAddress.data,
                                country=sellerForm.country.data,
                                user_id=current_user.id)
                
            db.session.add(new_seller)
            db.session.commit()
            flash("Seller registration successful", category="success")
            return redirect(url_for("seller"))
        
        else:
            flash("Error registering as a seller", category="error")

    if "submitBusinessDetails" in request.form:
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
            
    if seller and request.method == "GET":
        sellerForm.businessName.data = seller.business_name
        sellerForm.businessPhone.data = seller.business_phone
        sellerForm.businessAddress.data = seller.business_address
        sellerForm.country.data = seller.country
        

    if "submitNewListing" in request.form:
        if listingForm.validate_on_submit():
            new_listing = Listing(seller_id=seller.id,
                                  name=listingForm.name.data,
                                  description=listingForm.description.data,
                                  stock=listingForm.stock.data,
                                  price=listingForm.price.data,
                                  category=listingForm.category.data)
            
            db.session.add(new_listing)
            db.session.commit()
            
            if request.files.getlist("addImage"):
                upload_dir = os.path.join("app", "static", "product_images")

                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                for file in request.files.getlist("addImage"):
                    if file and file.filename:  # Ensure the file is valid
                        filename = secure_filename(file.filename)
                        if filename:  # Confirm filename isn't empty after securing
                            file_path = os.path.join(upload_dir, filename)
                            try:
                                file.save(file_path)
                                new_image = Image(product_id=new_listing.product_id,
                                                  url=os.path.join("product_images", filename))
                                db.session.add(new_image)
                                db.session.commit()                                
                            except:
                                flash(f"Error saving image {filename}", category="error")
            else:
                flash("Error uploading the image", category="error")
                                

            return redirect(url_for("seller"))

        else:
            flash("Error creating new listing: invalid product information.", category="error")

    existing_listings = []
    if seller:
        existing_listings = Listing.query.filter_by(seller_id=seller.id).all()

    return render_template("seller.html", sellerForm=sellerForm, listingForm=listingForm, user=user, seller=seller, listings=existing_listings)


@app.route("/edit_listing/<int:listing_id>", methods=["POST", "GET"])
@login_required
def editListing(listing_id):
    listing = Listing.query.filter_by(product_id=listing_id, seller_id=current_user.id).first()
    if not listing:
        flash("Listing not found or access unauthorized.", category="error")
        return redirect(url_for("seller"))

    form = CreateListingForm()

    if "updateListing" in request.form:
        if form.validate_on_submit():
            # Update listing details
            listing.name = form.name.data
            listing.description = form.description.data
            listing.stock = form.stock.data
            listing.price = form.price.data
            listing.category = form.category.data
            db.session.commit()


            if request.files.getlist("addImage"):
                upload_dir = os.path.join("app", "static", "product_images")

                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                for file in request.files.getlist("addImage"):
                    if file and file.filename:  # Ensure the file is valid
                        filename = secure_filename(file.filename)
                        if filename:  # Confirm filename isn't empty after securing
                            file_path = os.path.join(upload_dir, filename)
                            try:
                                file.save(file_path)
                                new_image = Image(product_id=listing.product_id,
                                                  url=os.path.join("product_images", filename))
                                db.session.add(new_image)
                                db.session.commit()
                                flash("Details updated successfully.", category="success")
                                
                            except:
                                flash(f"Error saving image {filename}", category="error")


            if "removeImages" in request.form:
                image_ids_to_remove = request.form.getlist("removeImages")
                current_images = Image.query.filter_by(product_id=listing_id).all()

                if len(current_images) <= len(image_ids_to_remove):
                    flash("Product listing must have at least one image.", category="error")
                else:
                    for image_id in image_ids_to_remove:
                        Image.query.filter_by(id=image_id).delete()
                        db.session.commit()

        else:
            flash("Error updating details: invalid product information.", category="error")
            
    if "deleteListing" in request.form:
        return redirect(url_for("deleteListing", listing_id=listing_id))

    images = Image.query.filter_by(product_id=listing_id).all()

    return render_template("edit_listing.html", listing=listing, form=form, user=current_user, images=images)


@app.route("/delete_listing/<int:listing_id>", methods=["POST", "GET"])
@login_required
def deleteListing(listing_id):
    listing = Listing.query.get(listing_id)
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    
    if not seller or listing.seller_id != seller.id:
        flash("You are not authorized to delete this listing", category="error")
        return redirect(url_for("seller"))
    
    Image.query.filter_by(product_id=listing.product_id).delete()
    Cart.query.filter_by(product_id=listing.product_id).delete()
    db.session.delete(listing)
    db.session.commit()
    
    flash("Listing deleted successfully", category="success")
    return redirect(url_for("seller"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
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
    
    return render_template("login.html", form=form, user=current_user)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        if form.password.data != request.form.get("passwordConfirmation"):
            flash("Passwords do not match.")
            return redirect("/signup")
        
        if User.query.filter_by(email=form.email.data).first():
            flash("An account with the email already exists.")
            return redirect("/signup")
               
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
    
    return render_template("sign_up.html", form=form, user=current_user)



