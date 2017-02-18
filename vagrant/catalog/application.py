from flask import Flask, render_template, request, redirect, url_for, jsonify
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

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

client_ID = '290206841222-r6nlpufcqg6supd67h4quuj2ekfqn4i7.apps.googleusercontent.com'
secret_key = 'VrdKYIFXxZ66u-YAJ2yit90M'
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

@app.route('/')
@app.route('/catalog')
def get_catalog():
    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(
                   Item.created_on.desc()).limit(5).all()
    return render_template('cataloglanding.html',
                           categories=categories,
                           items=latest_items)


@app.route('/catalog/json/')
def get_catalog_json():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/category/<int:category_id>/')
def get_category(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter(Category.id == category_id).first()
    return render_template('category.html',
                           categories=categories,
                           category=category)


@app.route('/category/<int:category_id>/json')
def get_category_json(category_id):
    category = session.query(Category).filter(Category.id == category_id).first()
    return jsonify(Category=[category.serialize])


@app.route('/category/<int:category_id>/<int:item_id>/')
def get_item(category_id, item_id):
    item = session.query(Item).filter(Item.item_id == item_id,
                                      Item.category_id == category_id).first()
    return render_template('item.html',
                           item=item)


@app.route('/item/<int:item_id>/json')
def get_item_json(item_id):
    item = session.query(Item).filter(Item.item_id == item_id).first()
    return jsonify(Item=[item.serialize])


@app.route('/item/<int:item_id>/update',
           methods=['GET', 'POST'])
def update_item(item_id):
    categories = session.query(Category).all()
    item = session.query(Item).filter(Item.item_id == item_id).first()

    if request.method == 'GET':
        return render_template('edititem.html', item=item,
                               categories=categories)
    else:
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        user_id = 1
        item.name = name
        item.description = description
        item.category_id = category
        item.user_id = user_id
        session.commit()

        return redirect(url_for('get_catalog'))


@app.route('/item/<int:item_id>/delete')
def delete_item(item_id):
    item = session.query(Item).filter(Item.item_id == item_id).first()
    session.delete(item)
    session.commit()
    return redirect(url_for('get_catalog'))


@app.route('/item/new', methods=['GET', 'POST'])
def add_item():

    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('newitem.html', categories=categories)
    else:
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        user_id = 1
        item = Item(name = name,
                    description = description,
                    category_id = category,
                    user_id = user_id)
        session.add(item)
        session.commit()

        return redirect(url_for('get_catalog'))


# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
