#!/usr/bin/python

from google.appengine.ext import ndb
import json

class Clients(ndb.Model):
	email = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	carts = ndb.KeyProperty(repeated = True)
	address = ndb.StringProperty()
	phone = ndb.StringProperty()

	
	def name2json(self):
		return {"name":self.name}

	def email2json(self):
		return {"email":self.email}
	

	def queryToName(self, client_key):
		name_carts = []
		cart_query = Carts.query(ancestor=client_key)
		for cart in cart_query:
			name_carts.append(cart.name2json())
		return name_carts	

	@classmethod
	def cartsANDitems(self, client_key):
		name_carts = []
		name_items = []
		cart_query = Carts.query(ancestor=client_key)
		for cart in cart_query:
			name_carts.append(cart.name2json())
			for item_key in cart.items:
				item = item_key.get()
				name_items.append(item.item2json())
			name_carts.append(name_items)
			name_items = []
		return name_carts 
	@classmethod
	def getName(self):
		return self.toJSONlist(Clients.query())

	@classmethod
	def toJSONlist(self, entriesList):
		auxJSON = []
		for item in entriesList:
			auxJSON.append(item.email2json())
		return auxJSON

	@classmethod
	def toJSONlistItems(self, entriesList):
		auxJSON = []
		for item in entriesList:
			auxJSON.append(item.name2json())
			auxJSON.append(item.items.to_dict())
		return auxJSON

class Carts(ndb.Model):
	name = ndb.StringProperty(required=True)
	items = ndb.KeyProperty(repeated=True)

	@classmethod
	def getName(self):
		return self.toJSONlist(Carts.query())


	def name2json(self):
		return {"name":self.name}

	@classmethod
	def items2json(self):
		return {"name":self.name, "items":self.items}
	
	@classmethod
	def toJSONlist(self, entriesList):
		auxJSON = []
		for item in entriesList:
			auxJSON.append(items.name2json())
		return auxJSON

class Wines(ndb.Model):
	name = ndb.StringProperty(required=True)
	wine_type = ndb.StringProperty(required=True)
	grade = ndb.FloatProperty()
	size = ndb.IntegerProperty()
	varietals = ndb.StringProperty()
	do = ndb.BooleanProperty()
	price = ndb.FloatProperty()
	photo = ndb.StringProperty()
	cask = ndb.StringProperty()
	bottle = ndb.StringProperty()
	

	def wine2json(self):
		return {"name":self.name}

	@classmethod
	def getWinesName(self):
		return self.toJSONlist(Wines.query())

	@classmethod
	def toJSONlist(self, entriesList):
		auxJSON = []
		for wine in entriesList:
			auxJSON.append(wine.wine2json())
		return auxJSON

class Items(ndb.Model):
	name = ndb.StringProperty(required=True)	
	
	@classmethod
	def toJSONlist(self, entriesList):
		auxJSON = []
		for item in entriesList:
			auxJSON.append(item.item2json())
		return auxJSON
		
	def item2json(self):
		return {"name":self.name}

