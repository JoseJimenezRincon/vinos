#/usr/bin/python
# -*- cod:ing: utf-8; mode: python -*-

#JoseJimenezRincon

from google.appengine.ext import ndb
from google.appengine.api import memcache
from flask import Flask, jsonify, abort, make_response, request, url_for



app = Flask(__name__)
app.config['DEBUG'] = True

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not Found'}), 404)

#---------------------------------Cliente--------------------------------#

@app.route('/clients', methods = ['GET', 'POST'])
def manager_clients():
	if request.method == 'POST':
		return newClient()
	elif request.method == 'GET':
		return getClients()

def newClient():
	if not request.json or not 'email' in request.json or not 'pass' in request.json:
		abort(400)
	email = request.json['title']
	password = request.json['pass']
	
	client = Client(
		email = email,
		password = password,
		carts = request.json.get('carts', []),
		address = request.json.get('address', ),
		phone = request.json.get('phone', ))

	idClient = client.put()
	memcache.flush_all()
	return make_response(jsonify({'created':idClient.urlsafe()}), 201)

def getClients():
	return make_response(jsonify({'clients':Clients.all()}), 200)


@app.route('/clients/<path:email>', methods = ['DELETE', 'PUT', 'GET'])
def manager_client(email):
	if request.method == 'DELETE':
		return deleteClient(email)
	elif request.method == 'PUT':
		return updateClient(email)
	elif request.method == 'GET':
		return getClientDetails(email)
	else:
		abort(404)

def deleteClient(email):
	try:
		client_key = ndb.Key(urlsafe=email)
	except:
		abort(404)
	client_key.delete()
	memcache.delete(email)	
	return make_response(jsonify({"deleted":email}), 200)

def updateClient(email):
	try:
		client_key = ndb.Key(urlsafe=email)
	except:
		abort(404)
	client = client_key.get()
	client.email = request.json.get('email', client.email)
        client.password = request.json.get('pass', client.password)
        client.carts = request.json.get('carts', client.carts)
        client.address = request.json.get('address', client.address)
        client.phone = request.json.get('phone', client.phone)
	client.put()
	memcache.flush_all()
	return make_response(jsonify({'updated':client.toJson()}), 200)

def getClientDetails(id_client):
	email = memcache.get(id_client)
	if email = None:
		try:
			client_key = ndb.Key(urlsafe=id_client)
		except:
			abort(404)
		client = client_key.get()
		email = client.email
		password = client.password
		carts = client.carts
		phone = client.phone	
	return make_response(jsonify({"email":email, "pass":password, "carts":carts, "phone":phone}))


@app.route('/clients/<path:email>/carts', methods = ['POST'])
def manager_cart_add(email):
	if request.method == 'POST':
		return addCart(email)
	else:
		abort(404)


def addCart(id_client):	
	if not request.json or not 'name' in request.json:
		abort(400)
	name = request.json['name']
	try:
		client_key = ndb.Key(urlsafe=id_client)
	except:
		abort(404)
	new_cart = Carts(
		parent = client_key
		name = name	
	}
	cart_id = new_cart.put()
	return make_response(jsonify({'created':cart_id.urlsafe())}), 201)


@app.route('/clients/<path:email>/carts/<path:cart_id>', methods = ['DELETE'])
def manager_cart_delete(cart_id):
	if request.method == 'DELETE':
		return deleteCart(cart_id)
	else:
		abort(404)


def deleteCart(cart_id):
	try:
		cart_key = ndb.Key(urlsafe=cart_id)
	except:
		abort(404)
	cart_key.delete()
	memcache.delete(cart_id)
	return	make_response(jsonify({'deleted':cart_id}), 200)


#-----------------------------CESTA-----------------------------#

@app.route('/clients/<path:email>/carts/<path:cart_id>/items', methods = ['GET', 'POST'])
def manager_items(cart_id):
	if request.method == 'GET':
		return getItems(cart_id)
	elif request.method == 'POST':
		return addItem(cart_id)
	else:
		abort(404)


def addItem(cart_id):
	if not request.json or not 'name' in request.json:
		abort(400)
	name = request.json['name']
	try:
		cart_key = ndb.Key(urlsafe=cart_id)
	except:
		abort(404)
	new_item = Items(
		parent = cart_key
		name = name
	)
	item_id = new_item.put()
	return make_response(jsonify({'added':item_id.urlsafe()}), 201)


def getItems(cart_id):
	auxJSON = []
	try:
		cart_key = ndb.Key(urlsafe=cart_id) #Entiendo que el cart_id es único.
	except:
		abort(404)
	ItemList = Items.query(ancestor=cart_key)
	auxJSON = Items.toJSONlist(ItemList)
	return make_response(jsonify({'items':auxJSON}), 200)


@app.route('/clients/<path:email>/carts/<path:cart_id>/items/<path:item_id>', methods = ['DELETE', 'PUT'])
def manager_item(item_id):
	if request.method == 'DELETE':
		return delItem(item_id)
	elif request.method == 'PUT':
		return updateItem(item_id)
	else:
		abort(404)
	

def delItem(item_id):
	try:
		item_key = ndb.Key(urlsafe=item_id) #Entiendo que el item_id es único.
	except:
		abort(404)
	item_key.delete()
	memcache.delete(item_id)
	return make_response(jsonify({'deleted':item_id}), 200)


def updateItem(item_id):
	try:
		item_key = ndb.Key(urlsafe=item_id)
	except:
		abort(404)
	item = item_key.get()
	item.parent = request.json.get('parent', item.parent)
	item.name = request.json.get('name', item.name)
	item.put()
	memcache.flush_all()
	return make_response(jsonify({'updated':item.toJson()}), 200)


#-----------------------------WINES-------------------------------#
	
@app.route('/wines', methods = ['DELETE', 'POST', 'GET'])
def manager_wines():
	
	if request.method == 'GET':
		if request.args.get('type'):
			return wineByType()
		if request.args.get('name'):
			return wineByName()
		if request.args.get('min'):
			return wineBetweenPrices()
	if request.method == 'POST':
		return addWine()
	elif request.method == 'DELETE':
		return deleteWine()
	elif request.method == 'GET':
		return allWines()
	else:
		abort(404)


def wineByType():
	if not request.args.get('type'):
		abort(400)
	wine_type = request.args.get('type')
	auxJSON = []
	winesByType = Wines.query(Wines.wine_type == wine_type)
	auxJSON = Wines.toJSONList(winesByType)
	return make_response(jsonify({'winesbytype':auxJSON}), 200)


def wineByName():	
	if not request.args.get('name'):
		abort(400)
	name = request.args.get('name')
	auxJSON = []
	winesByName = Wines.query(Wines.name == name)
	auxJSON = Wines.toJSONList(winesByName)
	return make_response(jsonify({'winesbyname':auxJSON}), 200)	

def wineBetweenPrices():
	if not request.args.get('min') or not request.args.get('max'):
		abort(400)
	minimum = request.args.get('min')
	maximum = request.args.get('max')
	auxJSON = [] 
	winesBetweenPrices = Wines.query(Wines.price >= minimum, Wines.price < maximum)
	auxJSON = wines.toJSONList(winesBetweenPrices)
	return make_response(jsonify({'winesbetweenprices':auxJSON}))


def addWine():
	if not request.json or not 'name' in request.json or not 'wine_type' in request.json:
	abort(400)
	name = request.json['name']
	wine_type = request.json['type']
	new_wine = Wines(
		name = name
		wine_type = wine_type
		grade = request.json.get('grade', )	
		size = request.json.get('size', )	
		varietals = request.json.get('varietals', )	
		do = request.json.get('do', )	
		price = request.json.get('price', )
		photo = request.json.get('photo', )
	)
	if wyne_type == 'Tinto':
		new_red_wine = RedWines(
			parent = new_wine.key,
			cask = request.json.get('cask', )
			bottle = request.json.get('bottle', )
		)
	wine_id = new_wine.put()
	new_red_wine.put()	
	return make_response(jsonify({'created':wine_id.urlsafe())}), 201)

def deleteWine(wine_id):
	try:
		wine_key = ndb.Key(urlsafe=wine_id) #Entiendo que el wine_id es único.
	except:
		abort(404)
	wine_key.delete()
	memcache.delete(wine_id)
	return make_response(jsonify({'deleted':wine_id}), 200)


def allWines():
	return make_response(jsonify({'wines':Wines.all()}))


@app.route('/wines/<int:wine_id>', methods = ['DELETE', 'PUT', 'GET'])
def manager_wine(wine_id):
	
	if request.method == 'GET':
		return getWineProperties(wine_id)
	elif request.method == 'PUT':
		return updateWine(wine_id)
	elif request.method == 'DELETE':
		return deleteWine(wine_id)
	else:
		abort(404)


def getWineProperties(wine_id):
	name = memcache.get(wine_id)
	auxJSON = []
	if name = None:
		try:
			wine_key = ndb.Key(urlsafe=wine_id)
		except:
			abort(404)
		wine = wine_key.get()
		name = wine.name
		wine_type = wine.wine_type
		grade = wine.grade	
		size = wine.size	
		varietals = wine.varietals
		do = wine.do	
		price = wine.price
		photo = wine.photo
		if wine_type == 'Tinto':
			for red_wine in RedWines.query(ancestor=wine_key):
				cask = red_wine.cask
				bottle = red_wine.bottle
	return jsonify({'name':name, 'type':wine_type, 'grade':grade, 'size':size, 'varietals':varietals, 'do':do, 'price':price, 'photo':photo,'cask':cask, 'bottle':bottle})

def updateWine(wine_id):
	try:
		wine_key = ndb.Key(urlsafe=wine_id)
	except:
		abort(404)
	wine = wine_key.get()
	wine.name = request.json.get('name', wine.name)
	wine.wine_type = request.json.get['type', wine.wine_type)
	wine.grade = request.json.get('grade', wine.grade)	
	wine.size = request.json.get('size', wine.size)	
	wine.varietals = request.json.get('varietals', wine.varietals)	
	wine.do = request.json.get('do', wine.do)	
	wine.price = request.json.get('price', wine.price)
	wine.photo = request.json.get('photo', wine.photo)
	wine.put()
	if wine.wine_type == 'Tinto':
		for red_wine in RedWines.query(ancestor=wine_key):
			red_wine.cask = request.json.get('cask', red_wine.cask)
			red_wine.bottle = request.json.get('bottle', red_wine.bottle)
		red_wine.put()
	memcache.flush_all()	
	return make_response(jsonify({'updated':wine.toJson()}), 200)


@app.route('/wines/<path:wine_type>', methods = ['GET'])
def manager_wine_type(wine_type):
	if request.method == 'GET':
		return wineByType(wine_type)
	else:
		abort(404)



@app.route('/search')
def search():
    name = request.args.get('name',"", type=str)
    wine_type = request.args.get('type',"", type=str)
    low_price = request.args.get('low_price',"0.0", type=str)
    high_price = request.args.get('high_price',"99999999.9", type=str)

    if name:
        return getWineByName(name)
    elif wine_type:
        return getWineByType(wine_type)
    elif low_price or high_price:
        return getWinesBetweenPrices(low_price, high_price)
    else:
        abort(404)

def getWinesByName(name):
    wines_json = Wines.toJSONlist(
        Wines.query(Wines.name==name))
    return make_response(jsonify({"wines":wines_json}), 200)

def getWinesByType(wine_type):
    wines_json = Wines.toJSONlist(
        Wines.query(Wines.wine_type==wine_type))
    return make_response(jsonify({"wines":wines_json}), 200)

def getWinesBetweenPrices(low_price, high_price):
    wines_json = Wines.toJSONlist(
        ndb.gql("SELECT * FROM Wines " +
                "WHERE price <= "+high_price+" AND price >= "+low_price))
    return make_response(jsonify({"wines":wines_json}), 200)
		
	
	
	
	


		

		
	
	

