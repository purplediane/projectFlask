from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///my_restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON API stuff here
@app.route('/restaurants/JSON')
def restaurantsJSON():
    places = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serialize for i in places])

@app.route('/restaurants/<int:restaurant_id>/JSON')
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(Restaurant=[restaurant.serialize], MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=[menuItem.serialize])

# End JSON API ENDPOINT HERE

@app.route('/')
@app.route('/restaurants')
@app.route('/restaurants/')
def showRestaurants():
    places = session.query(Restaurant).all()
    return render_template('restaurants.html', items=places)


@app.route('/restaurants/new', methods=['GET', 'POST'])
@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():
    print "newRestaurant"
    if request.method == 'POST':
        newRestaurant = Restaurant(
            name=request.form['name']
            )
        session.add(newRestaurant)
        session.commit()
        print "New restaurant added"
        flash("New restaurant created!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    print "editRestaurant, restaurant_id:", restaurant_id
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
            print "Restaurant changed"
            flash("Restaurant changed!")
        else:
            print "Not changed!"
            flash("Restaurant not changed!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant_id=restaurant_id, item = restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    print "deleteRestaurant, restaurant_id:", restaurant_id
    if request.method == 'POST':
        print "request.form:", request.form
        session.delete(restaurant)
        session.commit()
        flash("Restaurant deleted!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant_id=restaurant_id, item = restaurant)


@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    # There might be a better way to do this in the html, but I know how to do it here,
    # which will do for now.
    appetizers = []
    entrees = []
    desserts = []
    beverages = []
    other = []
    for item in menu_items:
        if item.course == "Appetizer":
            appetizers.append(item)
        elif item.course == "Entree":
            entrees.append(item)
        elif item.course == "Dessert":
            desserts.append(item)
        elif item.course == "Beverage":
            beverages.append(item)
        else:
            other.append(item)
    # Create list of labels and correspoding list of lists of items
    labels = []
    items = []
    if appetizers:
        labels.append("Appetizers")
        items.append(appetizers)
    if entrees:
        labels.append("Entrees")
        items.append(entrees)
    if desserts:
        labels.append("Desserts")
        items.append(desserts)
    if beverages:
        labels.append("Beverages")
        items.append(beverages)
    if other:
        labels.append("Other Items")
        items.append(other)
    num = len(labels)
    return render_template("menu.html", restaurant=restaurant, num=num, labels=labels, items=items)


@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    print "newMenuItem, restaurant_id:", restaurant_id
    if request.method == 'POST':
        newItem = MenuItem(
            name=request.form['name'], course=request.form['course'],
            description=request.form['description'],
            price=request.form['price'], restaurant_id=restaurant_id
            )
        session.add(newItem)
        session.commit()
        print "New menu item added"
        flash("New menu item created!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    print "editMenuItem, restaurant_id, menu_id:", restaurant_id, menu_id
    editItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        print "In edit, POST, new data is:"
        print "Name:", request.form['name'], "\nCourse:", request.form['course']
        print "Description:", request.form['description'], "\nPrice:", request.form['price']
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['course']:
            editItem.course = request.form['course']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['price']:
            editItem.price = request.form['price']
        session.add(editItem)
        session.commit()
        print "Menu item changed"
        flash("Menu item changed!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id,
            menu_id=menu_id, item=editItem)



@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    print "deleteMenuItem, restaurant_id, menu_id:", restaurant_id, menu_id
    deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        print "request.form:", request.form
        if request.form['delete']:
            session.delete(deleteItem)
            session.commit()
            flash("Menu item deleted!")
        else:
            flash("Menu item not deleted")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:

        return render_template('deletemenuitem.html', restaurant_id=restaurant_id,
            menu_id=menu_id, item=deleteItem)


if __name__ == '__main__':
    #print "Running the Flask server"
    app.secret_key = 'purple_dianes_lavender_key'
    app.debug = True
    # app.run(host='0.0.0.0', port=5000)
    app.run()
