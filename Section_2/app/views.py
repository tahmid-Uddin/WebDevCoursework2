from app import app, db, admin

from flask import render_template, flash, request, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user, login_required, logout_user, current_user
from flask_wtf.csrf import generate_csrf
from flask import send_file

from .models import User, Listing, Image, Cart, Seller, wishlist_table, Orders
from .forms import SignUpForm, LoginForm, UpdateUserForm, SellerRegistrationForm, CreateListingForm, ConfirmDeliveryDetailsForm

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import io
import datetime
import json


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Listing, db.session))
admin.add_view(ModelView(Image, db.session))
admin.add_view(ModelView(Cart, db.session))
admin.add_view(ModelView(Seller, db.session))
admin.add_view(ModelView(Orders, db.session))


@app.route("/")
def home():
    return redirect(url_for("adoption"))


def getProducts(category):
    """
    Used to retrieve relavent product info to display it to the user.

    Args:
        category (string): to filter which product category to return
    
    Returns:
        products (list): information of all products in the chosen category
    """
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
            product["images"].append(image.id)
            
        products.append(product)
    
    return products


@app.route('/image/<int:image_id>')
def renderImage(image_id):
    image = Image.query.get_or_404(image_id)
    return send_file(io.BytesIO(image.img), mimetype=image.mimetype, as_attachment=False, download_name=image.filename)


def searchListings(category, productsList, searchTerm,):
    """
    Finds all the similar products in the listing model, in the given 
    category that matches the given search term

    Args:
        category (string): filter which product category to return from
        productsList (list): list of all product details in the category
        searchTerm (string): user inputted search term

    Returns:
        _type_: _description_
    """
    
    # ilike for case insensitive implementation of SQL LIKE operator
    searchResults = Listing.query.filter(Listing.name.ilike(f"%{searchTerm}%")).all()
    
    searchResults = [result. name for result in searchResults if result.category == category]
    filteredProducts = [product for product in productsList if product["name"] in searchResults]
    
    return filteredProducts
    

@app.route("/adoption", methods=["POST","GET"])
def adoption():
    """
    Renders the adoption page with product listings and search bar
    implementation.
    """
    
    products = getProducts("adoption")
    title="Adopt a Pet Today!"
    userWishlist = []
    
    # Wishlist should only be available for logged in users.
    # Used to change state of wishlist "heart" icon - red and filled if
    # the product is the wish list, and grey otherwise.
    if current_user.is_authenticated:
        wishlistItems = db.session.query(wishlist_table).filter_by(id=current_user.id).all()
        userWishlist = [item.product_id for item in wishlistItems]
        
    if "submitSearch" in request.form:
        searchTerm = request.form["search"]
        
        # Updates products list to only included searched products
        products = searchListings("adoption", products, searchTerm)
        
        if not products:
            flash("No results found for search term.", category="error")
    
    return render_template("view_products.html", products=products, user=current_user, userWishlist=userWishlist, title=title)


@app.route("/accessories", methods=["GET", "POST"])
def accessories():
    """
    Renders the accessories page with product listings and search bar
    implementation. Similar to adoption() method.
    """
    products = getProducts("accessory")
    title = "Accessories"
    userWishlist = []
    
    # Wishlist should only be available for logged in users.
    # Used to change state of wishlist "heart" icon - red and filled if
    # the product is the wish list, and grey otherwise.
    if current_user.is_authenticated:
        wishlistItems = db.session.query(wishlist_table).filter_by(id=current_user.id).all()
        userWishlist = [item.product_id for item in wishlistItems]
        
    if "submitSearch" in request.form:
        searchTerm = request.form["search"]
        
        # Updates products list to only included searched products
        products = searchListings("accessory", products, searchTerm)
        
        if not products:
            flash("No results found for search term.", category="error")
    
    return render_template("view_products.html", products=products, user=current_user, userWishlist=userWishlist, title=title)


@app.route("/adoption/<int:listing_id>", methods=["POST", "GET"])
@app.route("/accesory/<int:listing_id>", methods=["POST", "GET"])
def listingPage(listing_id):
    """
    Given a listing_id, it displays all the product and seller information, and 
    gives the user the option to add to cart and add to wishlist.

    Args:
        listing_id (int): reference to a product listing in the Listing table (Listing.product_id)
    """
    
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
        product["images"].append(image.id)     

    # Wishlist should only be available for logged in users.
    # Used to change state of wishlist "heart" icon - red and filled if
    # the product is the wish list, and grey otherwise.
    if current_user.is_authenticated:
        wishlistItems = db.session.query(wishlist_table).filter_by(id=current_user.id, product_id=listing_id).all()
        userWishlist = [item.product_id for item in wishlistItems]  
    else:
        userWishlist = []


    return render_template("listing_page.html", product=product, seller=seller, user=current_user, image_count=len(product["images"]), userWishlist=userWishlist)


@app.route("/wishlist", methods=["POST", "GET"])
@login_required
def wishlist():
    """
    Displays all the products in the user's wishlist. 
    """
    
    wishlist = db.session.query(wishlist_table).filter_by(id=current_user.id).all()
    
    products=[]
    for item in wishlist:
        listing = Listing.query.filter_by(product_id=item.product_id).first()
        product = {
                "product_id": listing.product_id,
                "name": listing.name,
                "price": listing.price,
                "description": listing.description,
                "in_stock": listing.stock > 0,
                "image": None}
        
        # Only first image is retrieved, as multiple images don't need to be shown
        # in the wishlist - the products shown are clickable, and will take the user
        # to the listing page for the product.
        image = Image.query.filter_by(product_id=listing.product_id).first()
        
        product["image"] = (image.id)
        products.append(product)

        
    return render_template("wishlist.html", user=current_user, wishlist=products)


@app.route("/toggle_wishlist/<int:product_id>", methods=["POST"])
@login_required
def toggleWishlist(product_id):
    """
    Toggles the wishlist state of a given product for the current user.
    If the product is already in the wishlist, it removes it. If not, it adds it.

    Args:
        product_id (int): id of the product to toggle wishlist state

    Returns:
        _type_: _description_
    """
    # Check if item is already in wishlist.
    wishlist_item = db.session.query(wishlist_table).filter_by(id=current_user.id, product_id=product_id).first()
    if wishlist_item:
        # Removes item from the wishlist
        removeFromWishlist = wishlist_table.delete().where(wishlist_table.c.id == current_user.id, wishlist_table.c.product_id == product_id)
        db.session.execute(removeFromWishlist)
        db.session.commit()
        is_in_wishlist = False
        
    else:
        # Adds item to the wishlist
        addToWishlist = wishlist_table.insert().values(id=current_user.id, product_id=product_id)
        db.session.execute(addToWishlist)
        db.session.commit()
        is_in_wishlist = True
    
    # Generate a new CSRF token to be used for subsequent requests
    return json.dumps({"success": True, "in_wishlist": is_in_wishlist,"csrf_token": generate_csrf()})


@app.route("/cart", methods=["GET", "POST"])
def cart():
    """
    Displays all the products in the user's cart. If there are no items in the cart,
    it displays a message indicating so.
    """
    
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
            product["image"] = (image.id)
            products.append(product)
        
        total_price = sum([product["total_price"] for product in products if product["in_stock"]])
        total_quantity = sum([product["quantity"] for product in products if product["in_stock"]])
    
    else:
        products, total_price, total_quantity = None, None, None
            
    return render_template("cart.html", products=products, user=current_user, total_price=total_price, total_quantity=total_quantity)


@app.route("/add_to_cart/<int:listing_id>", methods=["POST"])
@login_required
def addToCart(listing_id):
    """
    Adds the specified quantity of a product to the user's cart. If the product is already in the cart,
    it updates the quantity. If the product is out of stock, it displays an error message.

    Args:
        listing_id (int): reference to a product listing in the Listing table
    """
    
    listing = Listing.query.filter_by(product_id=listing_id).first()
    itemAlreadyInCart = Cart.query.filter_by(user_id=current_user.id, product_id=listing_id).first()   
         
    if itemAlreadyInCart:
        newQuantity = itemAlreadyInCart.quantity + int(request.form.get("quantity", 1))
        
        #Checks if adding the extra quantity to the cart will put the product in negative stock.
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
        flash("Item(s) added to cart.", category="success")
        
    return redirect(url_for("listingPage", listing_id=listing_id))


@app.route("/deleteFromCart/<int:cart_id>", methods=["POST"])
@login_required
def deleteFromCart(cart_id):
    """
    Deletes the specified item from the user's cart.

    Args:
        cart_id (_type_): reference to an item in Cart Model to delete
    """
    
    Cart.query.filter_by(cart_id=cart_id).delete()
    db.session.commit()
    
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """
    Displays the checkout page, allowing the user to enter their delivery details.
    Only lets the user purchase the product if they have valid delivery address.
    
    Note: Since card checkout is not being implemented at this stage, the relavent
    database model, and user information will not be collected.
    """
    
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
            
            # Unique identifier for order is a combination of the user_id and the current
            # time. Since the same user can't make multiple orders at the same point in time,
            # these two identifiers will uniquely identify any order.
            datetime.datetime.now()
            cart = Cart.query.filter_by(user_id=current_user.id).all()
            order_time = datetime.datetime.now()
            
            for item in cart:
                product = Listing.query.filter_by(product_id=item.product_id).first()
                order = Orders(user_id=current_user.id,
                               product_name = product.name,
                               product_description = product.description,
                               product_price = product.price,
                               product_created_at = product.created_at,
                               seller_id=product.seller_id,
                               quantity=item.quantity,
                               order_time=order_time)
                
                db.session.add(order)
                
                #Reduces stock after order placed
                listing = Listing.query.filter_by(product_id=item.product_id).first()
                listing.stock -= item.quantity
                
                Cart.query.filter_by(cart_id=item.cart_id).delete()
                
                db.session.commit()
                
            flash("Successfully Placed Order", category="success")
            return redirect(url_for("pastOrders"))

    # Auto-fills content in the input fields, if they already exist the the database
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
    """
    Allows the user to update their personal details and also register as a seller.
    Seller and normal user will see different content - seller will see button to take
    them to seller dashboard while user will see seller registration form.
    
    Buttons to navigate to different pages include view past order history, view wishlist
    and seller dashboard/register as seller. 
    """
    
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
        
    # Auto-fills content if already exists in the database.
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
    """
    Allows the user to view all of the past orders they have placed.
    """
    
    userOrders = Orders.query.filter_by(user_id=current_user.id).all()
    pastOrders = []
    
    #Gets all the unique order identifier (time order placed)
    orderIdentifier = []
    for order in userOrders:
        if order.order_time not in orderIdentifier:
            orderIdentifier.append(order.order_time)
    
    #Most recent order shown first            
    orderIdentifier = reversed(sorted(orderIdentifier))

    # Groups orders by order identifier and gets details of each order.
    for identifier in orderIdentifier:
        orderGroup = Orders.query.filter_by(user_id=current_user.id, order_time=identifier).all()
        productsInOrder = []
        
        # Gets details of each product in the order and adds to productsInOrder list.
        for index, order in enumerate(orderGroup):
            
            # Order uses product information to store data about each product, rather than product id, to 
            # link itself to the product. This is because the latter would cause the record of the product
            # being ordered to be deleted, if the seller chooses to delete the product. Hence the first method
            # of using all product information to identify product ensures no data loss.
            product = {
                    "name": order.product_name,
                    "price": order.product_price,
                    "description": order.product_description,
                    "quantity": order.quantity,
                    "total_price": order.quantity * order.product_price,
                    "image": None,
                    "order_ref": None}
            
            # If the product is deleted, then there won't be any image data for the listing - if so, then a 
            # fixed "no_image" image is shown instead of a product image.
            try:
                listing = Listing.query.filter_by(name=order.product_name, description=order.product_description, price=order.product_price, created_at=order.product_created_at).first()
                image = Image.query.filter_by(product_id=listing.product_id).first()
                product["image"] = (image.id)
            except:
                
                product["image"] = "no_image"
            
            # Used to display the order reference - only done once for each order group, as the reference
            # (time of order) is the same for a particular order group
            if index == 0:
                product["order_ref"] = "".join([x for x in str(order.order_time) if x.isdigit()])
            
            productsInOrder.append(product)
            
        pastOrders.append(productsInOrder)

    return render_template("past_orders.html", pastOrders=pastOrders, user=current_user)


@app.route("/seller", methods=["GET", "POST"])
@login_required
def seller():
    """ 
    This function provides a seller dashboard where they can create listings, view and edit their 
    listings, see past orders users have placed for their store and edit their business information.
    """
    
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
            
            
    # Auto-fills business details.
    if seller and request.method == "GET":
        sellerForm.businessName.data = seller.business_name
        sellerForm.businessPhone.data = seller.business_phone
        sellerForm.businessAddress.data = seller.business_address
        sellerForm.country.data = seller.country
        

    if "submitNewListing" in request.form:
        if listingForm.validate_on_submit():
            images = request.files.getlist("addImage")
            
            # Must attach an image to a listing
            if images == []:
                flash("Error - must add atleast 1 image to the listing.", category="error")
                return redirect(url_for("seller"))
            
            else:
                for file in images:
                    # Sanitises filename so that it is safe to be stored on a server by removing
                    # harmful characters, and makes file compatible with other operating
                    # systems, by making filename use only ASCII characters
                    filename = secure_filename(file.filename)
                    
                    if "." in filename:
                        ext = filename.split(".")[1].lower()
                        
                        # Allows only certain file formats to be used.
                        if ext not in {"png", "jpg", "jpeg"}:
                            flash("Error - invalid image format.", category="error")
                            return redirect(url_for("seller"))

                # If all checks passed, then new listing is created.
                created_at = datetime.datetime.now()
                new_listing = Listing(seller_id=seller.id,
                                    name=listingForm.name.data,
                                    description=listingForm.description.data,
                                    stock=listingForm.stock.data,
                                    price=listingForm.price.data,
                                    category=listingForm.category.data,
                                    created_at=created_at)
                
                db.session.add(new_listing)
                db.session.commit()
                
                # Save images to app/static/product_images       
                if images:
                    for file in images:
                        # Ensure the file is valid
                        if file and file.filename:  
                            filename = secure_filename(file.filename)
                            
                            # Confirm filename isn't empty after securing - passes security check
                            if filename:
                                mimetype = file.mimetype                                  
                                try:
                                    
                                    new_image = Image(product_id=new_listing.product_id,
                                                      img=file.read(),
                                                      mimetype=mimetype,
                                                      filename=filename)
                                    db.session.add(new_image)
                                    db.session.commit()   
                                                                 
                                except:
                                    flash(f"Error saving image {filename}", category="error")
                                    return redirect(url_for("seller"))
                    
                    flash("Created listing successfully", category="success")
                    
                else:
                    flash("Error uploading the image", category="error")
                                
                return redirect(url_for("seller"))

        else:
            flash("Error creating new listing: invalid product information.", category="error")

    # Fetch existing listings from the database.
    existing_listings = []
    if seller:
        existing_listings = Listing.query.filter_by(seller_id=seller.id).all()

    return render_template("seller.html", sellerForm=sellerForm, listingForm=listingForm, user=user, seller=seller, listings=existing_listings)


@app.route("/edit_listing/<int:listing_id>", methods=["POST", "GET"])
@login_required
def editListing(listing_id):
    """
    Allows the user to edit a listing.

    Args:
        listing_id (int): reference to a product listing in Listing model.

    """
    
    listing = Listing.query.filter_by(product_id=listing_id, seller_id=current_user.id).first()
    if not listing:
        flash("Listing not found or access unauthorized.", category="error")
        return redirect(url_for("seller"))

    form = CreateListingForm()

    if "updateListing" in request.form:
        if form.validate_on_submit():
            listing.name = form.name.data
            listing.description = form.description.data
            listing.stock = form.stock.data
            listing.price = form.price.data
            listing.category = form.category.data
            
            flash("Product Information updated", category="success")
            db.session.commit()

            # Checks images have been attached
            images = request.files.getlist("addImage")
            if images:
                for file in images:
                    filename = secure_filename(file.filename)
                    
                    if "." in filename:
                        ext = filename.split(".")[1].lower()
                        
                        # Allows only certain file formats to be used.
                        if ext not in {"png", "jpg", "jpeg"}:
                            flash("Error - invalid image format.", category="error")
                            return redirect(url_for("seller"))

                for file in images:
                    # Ensure the file is valid
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        
                        # Confirm filename isn't empty - passes security check
                        if filename:                              
                            mimetype = file.mimetype                                  
                            try:
                                new_image = Image(product_id=listing.product_id,
                                                    img=file.read(),
                                                    mimetype=mimetype,
                                                    filename=filename)
                                db.session.add(new_image)
                                db.session.commit() 
                                
                            except:
                                flash(f"Error saving image {filename}", category="error")


            if "removeImages" in request.form:
                image_ids_to_remove = request.form.getlist("removeImages")
                current_images = Image.query.filter_by(product_id=listing_id).all()
                
                # Listing must have at least one image
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

    # Used to display all the existing product images, so that the user can choose to delete them.
    images = Image.query.filter_by(product_id=listing_id).all()

    return render_template("edit_listing.html", listing=listing, form=form, user=current_user, images=images)


@app.route("/delete_listing/<int:listing_id>", methods=["POST", "GET"])
@login_required
def deleteListing(listing_id):
    """_summary_

    Args:
        listing_id (_type_): reference to a product which the selelr wants to delete
    """
    
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
    """
    Checks the users log in details, and if they are correct, logs them into the 
    website, giving them access to more features.
    """
    form = LoginForm()
    
    if form.validate_on_submit(): 
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
    """
    Lets a new user sign up to the platform.
    """
    
    form = SignUpForm()
    
    if form.validate_on_submit():
        if form.password.data != request.form.get("passwordConfirmation"):
            flash("Passwords do not match.")
            return redirect("/signup")
        
        if User.query.filter_by(email=form.email.data).first():
            flash("An account with the email already exists.")
            return redirect("/signup")

        # If multiple names in the first name field, breaks it down so that the
        # first name is the first name, and the rest are middle name.
        name = form.firstName.data.split(" ")
        if len(name) == 1: 
            middleName = None 
        else: 
            middleName = " ".join([x.capitalize() for x in name[1:]])
            
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



