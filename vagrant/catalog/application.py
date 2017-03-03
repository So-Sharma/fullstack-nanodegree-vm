from flask import Flask, render_template, request, \
    redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

secret_key = 'VrdKYIFXxZ66u-YAJ2yit90M'
CLIENT_ID = json.loads(
   open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

# Make login_session available to templates
app.jinja_env.globals['login_session'] = login_session


# Function to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            flash('Please log in to add/update an item')
            return redirect(url_for('get_catalog'))
        return f(*args, **kwargs)
    return decorated_function


# Displays the catalog landing/home page
@app.route('/')
@app.route('/catalog')
def get_catalog():
    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(
                   Item.created_on.desc()).limit(5).all()
    return render_template('cataloglanding.html',
                           categories=categories,
                           items=latest_items)


# A JSON end point that serves the details of the catalog
@app.route('/catalog/json/')
def get_catalog_json():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


# Displays the category details page
@app.route('/category/<int:category_id>/')
def get_category(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter(
                            Category.id == category_id).first()
    return render_template('category.html',
                           categories=categories,
                           category=category)


# A JSON end point that serves the details of a category
@app.route('/category/<int:category_id>/json')
def get_category_json(category_id):
    category = session.query(Category).filter(
        Category.id == category_id).first()
    return jsonify(Category=[category.serialize])


# Displays the Items details page
@app.route('/category/<int:category_id>/<int:item_id>/')
def get_item(category_id, item_id):
    item = session.query(Item).filter(Item.item_id == item_id,
                                      Item.category_id == category_id).first()
    return render_template('item.html',
                           item=item)


# A JSON end point that serves the details of an item in the catalog
@app.route('/item/<int:item_id>/json')
def get_item_json(item_id):
    item = session.query(Item).filter(Item.item_id == item_id).first()
    return jsonify(Item=[item.serialize])


# Allows the user to update the details of an item in the catalog
@app.route('/item/<int:item_id>/update',
           methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    categories = session.query(Category).all()
    item = session.query(Item).filter(Item.item_id == item_id).first()

    if request.method == 'GET':
        return render_template('edititem.html', item=item,
                               categories=categories)
    else:
        if item.user_id != login_session['user_id']:
            flash('You do not have permission to edit the item details')
        else:
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']
            user_id = login_session['user_id']
            if not (name and description and category and user_id):
                flash('One or more fields are blank')
            else:
                item.name = name
                item.description = description
                item.category_id = category
                item.user_id = user_id
                session.commit()
                return redirect(url_for('get_catalog'))

        return redirect(url_for('update_item', item_id=item_id))


# Allows a user to delete an item
@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if request.method == 'GET':
        item = session.query(Item).filter(Item.item_id == item_id).first()
        return render_template('deleteitemconfirm.html',
                               item=item)
    else:
        item = session.query(Item).filter(Item.item_id == item_id).first()
        if item.user_id != login_session['user_id']:
            flash('You do not have permission to delete the item')
        else:
            # Delete item from the database
            session.delete(item)
            session.commit()
            return redirect(url_for('get_catalog'))
        return redirect(url_for('update_item', item_id=item_id))


# Allows a user to add an item
@app.route('/item/new', methods=['GET', 'POST'])
@login_required
def add_item():

    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('newitem.html', categories=categories)
    else:
        error = None
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        user_id = login_session['user_id']
        if not (name and description and category and user_id):
            error = 'One or more fields are blank'
            categories = session.query(Category).all()
            return render_template('newitem.html', error=error,
                                   categories=categories)
        else:
            # Add item to the database
            item = Item(name=name,
                        description=description,
                        category_id=category,
                        user_id=user_id)
            session.add(item)
            session.commit()

        categories = session.query(Category).all()
        latest_items = session.query(Item).order_by(
           Item.created_on.desc()).limit(5).all()

        return render_template('cataloglanding.html', error=error,
                               categories=categories,
                               items=latest_items)


# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# User sign-in and authentication using Google api
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode("utf8"))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if the user has already been added to the db.
    # If not, add user details to the DB
    user = session.query(User).filter(
        User.email == login_session['email']).first()
    if not user:
        new_user = User(name=login_session['username'],
                        email=login_session['email'])
        session.add(new_user)
        session.commit()
        login_session['user_id'] = new_user.id
    else:
        login_session['user_id'] = user.id
    return 'Welcome'


# This is for logging out a user
@app.route('/gdisconnect')
def gdisconnect():
    login_session.clear()
    flash('Log out successful')
    return redirect(url_for('get_catalog'))


# Application details
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
