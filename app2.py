from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['DSMarkets']

# Choose collections
products = db['Products']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(email):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (email, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions

"""
    #Optional functions to check the users and products that have been added to the database

    @app.route('/getAllUsers', methods=['GET'])
    def get_all_users():
        iterable = users.find({})
        output = []
        for user in iterable:
            user['_id'] = None
            output.append(user)
        return jsonify(output)

    @app.route('/getAllProducts', methods=['GET'])
    def get_all_products():
        iterable = products.find({})
        output = []
        for product in iterable:
            product['_id'] = None
            output.append(product)
        return jsonify(output)
"""

#ΕΓΓΡΑΦΗ ΧΡΗΣΤΗ ΣΤΟ ΣΥΣΤΗΜΑ (ΔΙΑΧΕΙΡΙΣΤΗΣ)-------------------------------------------------------------------------------------------------------------------------------
@app.route('/createUserAdmin', methods=['POST'])
def create_user_admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "name" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    #Checking if there are any other users with the same email address
    if users.find({"email":data['email']}).count() == 0:
        #Passing the login information to dictionary user
        user = {"email":data['email'], "name":data['name'], "password":data['password']}
        #Inserting user to database
        users.insert_one(user)
        #Creating key "category" for the user with key value 'admin'
        users.update_one({"email":data['email']}, 
                {"$set":
                     {
                        "category":'admin'
                    }
                })
        #Success response if the query executed successfully and user was added to database
        return Response(data['name']+" was added to the MongoDB.\n", status=200, mimetype='application/json')
    #A user with the same email address was found
    else:
        #Error response if a user with the same email address already exist
        return Response("A user with the given email already exists.\n", status=400, mimetype='application/json')

#ΕΓΓΡΑΦΗ ΧΡΗΣΤΗ ΣΤΟ ΣΥΣΤΗΜΑ (ΑΠΛΟΣ ΧΡΗΣΤΗΣ)------------------------------------------------------------------------------------------------------------------------------
@app.route('/createUserCustomer', methods=['POST'])
def create_user_customer():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "name" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Checking if there are any other users with the same email address
    if users.find({"email":data['email']}).count() == 0:
        #Passing the login information to dictionary user
        user = {"email":data['email'], "name":data['name'], "password":data['password']}
        #Inserting user to database
        users.insert_one(user)
        #Creating key "category" for the user with key value 'customer'
        users.update_one({"email":data['email']}, 
                {"$set":
                    {
                        "category":'customer'
                    }
                })
        #Success response if the query executed successfully and user was added to database
        return Response(data['name']+" was added to the MongoDB.\n", status=200, mimetype='application/json')
    #A user with the same username was found
    else:
        #Error response if a user with the same email address already exist
        return Response("A user with the given email already exists.\n", status=400, mimetype='application/json')
    
#ΕΙΣΟΔΟΣ ΣΤΟ ΣΥΣΤΗΜΑ-----------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding a user with the given email and password
    user = users.find_one({"$and":[ {"email":data['email']}, {"password":data['password']}]})

    #Checking if user with the given username and password exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Calling function create_session and passing its return value to variable user_uuid 
            user_uuid = create_session(data['email'])
            #Passing the user's uuid and username information to dictionary res
            res = {"uuid": user_uuid, "email": data['email']}
            #Success response containing phrase "Successful login" alongside user's uuid and username
            return Response("Successful login "+ json.dumps(res),status=200, mimetype='application/json')
            #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer.\n", status=400, mimetype='application/json')
    #Authentication failed
    else:
        #Error response if user's information are not correct
        return Response("Wrong mail or password.\n", status=400, mimetype='application/json')

#ΑΝΑΖΗΤΗΣΗ ΠΡΟΙΟΝΤΟΣ-----------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/getProduct', methods=['GET'])
def get_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    if not "name" in data and not "category" in data and not "product_id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    if (("name" in data) and ("product_id" in data)) or (("name" in data) and ("category" in data)) or (("product_id" in data) and ("category" in data)) or (("name" in data) and ("product_id" in data) and ("category" in data)):
        return Response("Only one field needed",status=500,mimetype="application/json")
    
    #Finding a user with the given email
    user = users.find_one({"email":data['email']})

    #Checking if user exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Passing user's uuid to variable uuid
            uuid = request.headers.get('authorization')
            #Calling function is_session_valid with parameter uuid and passing its return value to variable authentication
            authentication = is_session_valid(uuid)
            #Authentication failed
            if (authentication == False):
                #Error response
                return Response("Authentication Failed\n", status=401, mimetype='application/json')
            #Authentication successful
            else:
                #Searching by product_id
                if "product_id" in data:
                    #Finding a product with the given product_id
                    product = products.find_one({"product_id":{"$eq":data['product_id']}})
                    #Checking if product exists
                    if product == None:
                        #Response if no product was found
                        return Response("No product with that id was found.\n", mimetype='application/json')
                    #There is a product in the database with that id
                    else:
                        product['_id'] = None
                        #Response if query executed successfully
                        return Response(json.dumps(product), status=200, mimetype='application/json')
                #Searching by name
                elif "name" in data:
                    #Checking if there are products in the db with the given name
                    if (products.find({"name":{"$eq":data['name']}}).count() == 0):
                        #Response if no product was found
                        return Response("No product with that name was found.\n", mimetype='application/json')
                    #There is at least one product in the database with that name
                    else:
                        #Assigning to iterable all of the products with value of key 'name' equal to the product's name given by the user
                        iterable = products.find({"name":{"$eq":data['name']}})
                        #Declaring empty list to be filled with products
                        products_list = []
                        #Iterating through iterable and appending to products_list every one of itetable's products
                        for product in iterable:
                            product['_id'] = None
                            products_list.append(product)
                        #Response if query executed successfully
                        return Response(json.dumps(products_list, indent=4), status=200, mimetype='application/json')
                #Searching by category
                elif "category" in data:
                    #Checking if there are products in the db that belong in the given category
                    if (products.find({"category":{"$eq":data['category']}}).count() == 0):
                        #Response if no product was found
                        return Response("No product in that category was found.\n", mimetype='application/json')
                    #There is at least one product in the database that belongs to the given category
                    else:
                        #Assigning to iterable all of the products with value of key 'category' equal to the product's category given by the user
                        iterable = products.find({"category":{"$eq":data['category']}})
                        #Declaring empty list to be filled with products
                        products_list = []
                        #Iteratting through iterable and appending to products_list every one of itetable's products
                        for product in iterable:
                            product['_id'] = None
                            products_list.append(product)
                        #Sorting products_list in ascending order
                        for i in range (0, len(products_list)):
                            for j in range(len(products_list)-1, i, -1):
                                if (products_list[j].get("price")) < (products_list[j-1].get("price")):
                                    temp1 = products_list[j]
                                    products_list[j] = products_list[j-1]
                                    products_list[j-1] = temp1
                        #Response if query executed successfully
                        return Response(json.dumps(products_list, indent=4), status=200, mimetype='application/json')
        #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer.\n", status=400, mimetype='application/json')
    else:
        #Response if there is no user with the given email
        return Response("No user with that email was found.\n", status=500, mimetype='application/json')

#ΠΡΟΣΘΗΚΗ ΠΡΟΙΟΝΤΩΝ ΣΤΟ ΚΑΛΑΘΙ-------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/addToCart', methods=['PATCH'])
def add_to_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "product_id" in data or not "quantity" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding user with the given email address
    user = users.find_one({"email":data['email']})
    #Finding product with given product_id
    product = products.find_one({"product_id":data['product_id']})
    
    #Checking if user exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Passing user's uuid to variable uuid
            uuid = request.headers.get('authorization')
            #Calling function is_session_valid with parameter uuid and passing its return value to variable authentication
            authentication = is_session_valid(uuid)
            #Authentication failed
            if (authentication == False):
                #Error response
                return Response("Authentication Failed\n", status=401, mimetype='application/json')
            #Authentication successful
            else:
                #Checking if product exists
                if product != None:
                    #Checking if the given quantity is less than the product's stock
                    if int(data['quantity']) <= int(product['stock']):
                        #If key cart doesn't exist in dictionary user
                        if not 'cart' in user:
                            #Declaring list cart_list with default value 0 for the first element
                            cart_list = [0]
                            #Appending to cart_list a dictionary with one key-value pair, where key's name is the product's id and key's value is the given quantity 
                            cart_list.append({product["product_id"]:data["quantity"]})
                            #Assigning to the first element of the list the price of the products
                            cart_list[0] = cart_list[0]+float(product['price'])*float(data['quantity'])
                            #Adding a 'cart' key to user's dictionary with key-value the cart_list
                            users.update_one({"email":data['email']}, 
                                    {"$set":
                                        {
                                            "cart":cart_list
                                        }
                                    })
                            #Assigning to total var the price
                            total = cart_list[0]
                            #Removing price from the cart_list in order to print separately 
                            cart_list.pop(0)
                        #If 'cart' key exists in user's dictionary
                        else:
                            #Assigning the value of key 'cart' to cart_list
                            cart_list = user['cart']
                            #Iterating through the cart_list to check if there's already a product with the same product_id
                            for i in range(1, len(cart_list)):
                                if list(cart_list[i].keys())[0] == data['product_id']:
                                    #Returning a corresponding response
                                    return Response("Product has already been added to cart\n", status=400, mimetype='application/json')
                            #Appending to cart_list a dictionary with one key-value pair, where key's name is the product's id and key's value is the given quantity
                            cart_list.append({product["product_id"]:data["quantity"]})
                            #Assigning to the first element of the list the new total price
                            cart_list[0] = cart_list[0]+float(product['price'])*float(data['quantity'])
                            #Updating 'cart' key of user's dictionary 
                            users.update_one({"email":data['email']}, 
                                    {"$set":
                                        {
                                            "cart":cart_list
                                        }
                                    })
                            #Assigning to total var the new priceprice
                            total = user['cart'][0]
                            #Removing price from the cart_list in order to print separately
                            cart_list.pop(0)
                        #Success response if the query executed successfully and product was added to database
                        return Response("The product with id = " + data['product_id'] +" was added to cart.\n +-+-+-+-+ CART +-+-+-+\n Product ID : Quantity\n" +json.dumps(cart_list, indent=4) + "\nTotal: " + json.dumps(total) + "€\n", status=200, mimetype='application/json')
                    #There is no sufficient stock
                    else:
                        #Error response if there is insufficient stock
                        return Response("No sufficient stock.\n", status=500, mimetype='application/json')
                else:
                    #Error response if product doesn't exists
                    return Response("No product with that id was found.\n", status=500, mimetype='application/json')
        #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer\n", status=400, mimetype='application/json')
    else:
        #Response if there is no user with the given email
        return Response("No user with that email was found\n", status=500, mimetype='application/json')

#ΕΜΦΑΝΙΣΗ ΚΑΛΑΘΙΟΥ-------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/viewCart', methods=['GET'])
def view_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding user with the given email address
    user = users.find_one({"email":data['email']})

    #Checking if user exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Passing user's uuid to variable uuid
            uuid = request.headers.get('authorization')
            #Calling function is_session_valid with parameter uuid and passing its return value to variable authentication
            authentication = is_session_valid(uuid)
            #Authentication failed
            if (authentication == False):
                #Error response
                return Response("Authentication Failed\n", status=401, mimetype='application/json')
            #Authentication successful
            else:
                #If 'cart' key exists in user's dictionary
                if 'cart' in user:
                    #Assigning the value of key 'cart' to cart_list
                    cart_list = user['cart']
                    #Assigning to total var the new priceprice
                    total = user['cart'][0]
                    #Removing price from the cart_list in order to print separately
                    cart_list.pop(0)
                    #Success response if the query executed successfully
                    return Response(" +-+-+-+-+ CART +-+-+-+\n Product ID : Quantity\n" +json.dumps(cart_list, indent=4) + "\nTotal: " + json.dumps(total) + "€\n", status=200, mimetype='application/json')
                #If key cart doesn't exist in dictionary user
                else:
                    #Returning the corresponding response
                    return Response("User's cart is empty\n", status=400, mimetype='application/json')
        #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer\n", status=400, mimetype='application/json')
    else:
        #Response if there is no user with the given email
        return Response("No user with that email was found\n", status=500, mimetype='application/json')

#ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΚΑΛΑΘΙ----------------------------------------------------------------------------------------------------------------------------------------
@app.route('/deleteFromCart', methods=['PATCH'])
def delete_from_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "product_id" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding user with the given email address
    user = users.find_one({"email":data['email']})
    #Finding product with given product_id
    product = products.find_one({"product_id":data['product_id']})
    #Initializing cart_list_index var with None
    cart_list_index = None

    #Checking if user exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Passing user's uuid to variable uuid
            uuid = request.headers.get('authorization')
            #Calling function is_session_valid with parameter uuid and passing its return value to variable authentication
            authentication = is_session_valid(uuid)
            #Authentication failed
            if (authentication == False):
                #Error response
                return Response("Authentication Failed\n", status=401, mimetype='application/json')
            #Authentication successful
            else:
                #If key cart doesn't exist in dictionary user
                if not 'cart' in user:
                    #Returning the corresponding response
                    return Response("User's cart is empty\n", status=500, mimetype='application/json')
                #If 'cart' key exists in user's dictionary
                else:
                    #Checking if product exists
                    if product != None:
                        #Assigning the value of key 'cart' to cart_list
                        cart_list = user['cart']
                        #Checking if there is a key in user's cart with name equal to the value of the product_id given by the user
                        for i in range(1, len(cart_list)):
                            if list(cart_list[i].keys())[0] == data['product_id']:
                                cart_list_index = i
                                break
                        #Checking if there is a product with the product_id given by the user
                        if cart_list_index != None:
                            #Updating the total price by subsctracting the price of the products to be deleted
                            cart_list[0] = cart_list[0] - float(product['price'])*float(cart_list[cart_list_index].get(data['product_id']))
                            #Removing the product from the cart_list
                            cart_list.pop(cart_list_index)
                            #Checking if cart_list has only one element (price element-->0)
                            if len(cart_list) == 1:
                                #Updating 'cart' key of user's dictionary
                                users.update_one({"email":data['email']}, 
                                            {"$unset":
                                                {
                                                    "cart":""
                                                }
                                            })
                            else:
                                #Removing 'cart' key from user's dictionary
                                users.update_one({"email":data['email']}, 
                                    {"$set":
                                        {
                                            "cart":cart_list
                                        }
                                    })
                            #Assigning to total var the new priceprice
                            total = user['cart'][0]
                            #Removing price from the cart_list in order to print separately
                            cart_list.pop(0)
                            #Success response if the query executed successfully
                            return Response("Product with id = " +data['product_id']+" was deleted.\n +-+-+-+-+ CART +-+-+-+\n Product ID : Quantity\n" +json.dumps(cart_list, indent=4) + "\nTotal: " + json.dumps(total) + "€\n",status=200, mimetype='application/json')
                        else:
                            #Error response if product doesn't exists in user's cart
                            return Response("No product with that id was found in user's cart\n", status=500, mimetype='application/json')
                    else:
                        #Error response if product doesn't exists
                        return Response("No product with that id was found\n", status=500, mimetype='application/json')
        #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer\n", status=400, mimetype='application/json')
    else:
        #Response if there is no user with the given email
        return Response("No user with that email was found\n", status=500, mimetype='application/json')

#ΑΓΟΡΑ ΠΡΟΙΟΝΤΩΝ---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/buy', methods=['PATCH'])
def buy():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "card_number" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding user with the given email address
    user = users.find_one({"email":data['email']})
    
    #Checking if user exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Passing user's uuid to variable uuid
            uuid = request.headers.get('authorization')
            #Calling function is_session_valid with parameter uuid and passing its return value to variable authentication
            authentication = is_session_valid(uuid)
            #Authentication failed
            if (authentication == False):
                #Error response
                return Response("Authentication Failed\n", status=401, mimetype='application/json')
            #Authentication successful
            else:
                #Declaring list orders to store user's orders
                orders = []
                #Creating card_number cart to store user's card number
                card_number = data["card_number"]
                #Checking if card number's length is exactly 16 digits
                if len(card_number) != 16:
                    #Error response if card number has more/less than 16 digits
                    return Response("Not valid card number.\n", status=500, mimetype='application/json')
                #If card number's length is 16 digits
                else:  
                    #Checking if 'cart' key exists in user's dictionary
                    if 'cart' in user:
                        #Checking 'order_history' key exists in user's dictionary
                        if not 'order_history' in user:
                            #Assigning the value of key 'cart' to cart_list
                            cart_list = user['cart']
                            #Appending recent cart to orders list
                            orders.append(cart_list)
                            #Assigning to total var the new price
                            total = user['cart'][0]
                            #Updating 'cart' key of user's dictionary
                            users.update_one({"email":data['email']},
                                {"$set":
                                    {
                                        "order_history":orders
                                    }
                                })
                            #Removing the 'cart' key from user's dictionary
                            users.update_one({"email":data['email']}, 
                                            {"$unset":
                                                {
                                                    "cart":""
                                                }
                                            })
                            #Removing price from the cart_list in order to print separately
                            cart_list.pop(0)
                        else:
                            #Assigning the value of key 'order_history' to orders list
                            orders = user['order_history']
                            #Assigning the value of key 'cart' to cart_list
                            cart_list = user['cart']
                            #Appending recent cart to orders list
                            orders.append(cart_list)
                            #Assigning to total var the new price
                            total = user['cart'][0]
                            #Updating 'order history' key of user's dictionary
                            users.update_one({"email":data['email']},
                                {"$set":
                                    {
                                        "order_history":orders
                                    }
                                })
                            #Removing the 'cart' key from user's dictionary
                            users.update_one({"email":data['email']}, 
                                            {"$unset":
                                                {
                                                    "cart":""
                                                }
                                            })
                            #Removing price from the cart_list in order to print separately
                            cart_list.pop(0)
                        #Success response if the query executed successfully
                        return Response("Thank you for your purchase...Here is the receipt:\n +-+-+-+ RECEIPT +-+-+\n Product ID : Quantity\n" +json.dumps(cart_list, indent=4) + "\nTotal: " + json.dumps(total) + "€\n", status=200, mimetype='application/json')
                    #If key cart doesn't exist in dictionary user
                    else:
                        #Returning the corresponding response
                        return Response("User's cart is empty\n", status=500, mimetype='application/json')
        #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer\n", status=400, mimetype='application/json')     
    else:
        #Response if there is no user with the given email
        return Response("No user with that email was found\n", status=500, mimetype='application/json')

#ΕΜΦΑΝΙΣΗ ΙΣΤΟΡΙΚΟΥ ΠΑΡΑΓΓΕΛΙΩΝ------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/viewOrderHistory', methods=['GET'])
def view_order_history():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding user with the given email address
    user = users.find_one({"email":data['email']})
    
    #Checking if user exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Passing user's uuid to variable uuid
            uuid = request.headers.get('authorization')
            #Calling function is_session_valid with parameter uuid and passing its return value to variable authentication
            authentication = is_session_valid(uuid)
            #Authentication failed
            if (authentication == False):
                #Error response
                return Response("Authentication Failed\n", status=401, mimetype='application/json')
            #Authentication successful
            else:
                #If 'order history' key exists in user's dictionary
                if 'order_history' in user:
                    #Assigning the value of key 'order_history' to order_history_list
                    order_history_list = user['order_history']
                    #Success response if the query executed successfully
                    return Response("Here is your order history:\n" +json.dumps(order_history_list, indent=4), status=200, mimetype='application/json')
                #If key 'order_history' doesn't exist in dictionary user
                else:
                    #Error response if user hasn't placed any orders
                    return Response("You haven't placed any orders", status=400, mimetype='application/json')
        #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer\n", status=400, mimetype='application/json')
    else:
        #Response if there is no user with the given email
        return Response("No user with that email was found\n", status=500, mimetype='application/json')

#ΔΙΑΓΡΑΦΗ ΛΟΓΑΡΙΑΣΜΟΥ----------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/deleteUser', methods=['DELETE'])
def delete_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Searching in students collection for a user with the given email 
    user = users.find_one({"email":data['email']})

    #Checking if the user with the given email exists
    if user != None:
        #Checking if user is a customer
        if user['category'] == "customer":
            #Passing user's uuid to variable uuid
            uuid = request.headers.get('authorization')
            #Calling function is_session_valid with parameter uuid and passing its return value to variable authentication
            authentication = is_session_valid(uuid)
            #Authentication failed
            if (authentication == False):
                #Error response
                return Response("Authentication Failed\n", status=401, mimetype='application/json')
            #Authentication successful
            else:
                #Deleting the user from the collection
                users.delete_one(user)
                #Passing the user's name and the string " was deleted" to variable msg
                msg = user['name'] + " was deleted\n"
                #Response if query executed successfully
                return Response(msg, status=200, mimetype='application/json')
        #User's category is not 'customer'
        else:
            #Error response if user is not a customer
            return Response("User is not a customer\n", status=400, mimetype='application/json')
    #There is no user with the given email
    else:
        #Response if there is no user with the given email
        return Response("No user with that email was found\n", status=500, mimetype='application/json')

#ΕΙΣΑΓΩΓΗ ΝΕΟΥ ΠΡΟΙΟΝΤΟΣ-------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/addProduct', methods=['POST'])
def add_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "product_id" or not "description" in data or not "category" in data or not "stock" in data or not "price" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding user with the given email address
    user = users.find_one({"email":data['email']})
    #Finding product with given product_id
    product = products.find_one({"product_id":data['product_id']})

    #Checking if user is an admin
    if user['category'] == "admin":
        #Checking if there is already a product with the same id in the database
        if product == None:
            #Passing the product information to dictionary product
            product = {"product_id":data['product_id'], "name":data['name'], "category":data['category'], "stock":data['stock'], "description":data['description'], "price":data['price']}
            #Inserting product to database
            products.insert_one(product)
            #Success response if the query executed successfully and product was added to database
            return Response(data['name']+" was added to the MongoDB\n", status=200, mimetype='application/json')
        else:
            #Error response if a product with the same id already exist
            return Response("A product with the given id already exists\n", status=400, mimetype='application/json')
    #User's category is not 'admin'
    else:
        #Error response if user is not an admin
        return Response("User is not an admin\n", status=400, mimetype='application/json')

#ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΣΥΣΤΗΜΑ---------------------------------------------------------------------------------------------------------------------------------------
@app.route('/deleteProduct', methods=['DELETE'])
def delete_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "product_id" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    #Finding user with the given email address
    user = users.find_one({"email":data['email']})
    #Finding product with given product_id
    product = products.find_one({"product_id":data['product_id']})

    #Checking if user is an admin
    if user['category'] == "admin":
        #Checking if the product with the given id exists
        if product != None:
            #Deleting the product from the collection
            products.delete_one(product)
            #Passing the product's name and the string " was deleted" to variable msg
            msg = product['name'] + " was deleted\n"
            #Response if query executed successfully
            return Response(msg, status=200, mimetype='application/json')
        #There is no product with the given product_id
        else:
            #Response if there is no product with the given id
            return Response("No product with that id was found\n", status=500, mimetype='application/json')
    #User's category is not 'admin'
    else:
        #Error response if user is not an admin
        return Response("User is not an admin\n", status=400, mimetype='application/json')

#ΕΝΗΜΕΡΩΣΗ ΠΡΟΙΟΝΤΟΣ-----------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/updateProduct', methods=['PATCH'])
def update_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "product_id" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    if (not "name" in data) and (not "price" in data) and (not "stock" in data) and (not "description" in data):
        return Response("Information incomplete, name or price or stock or description needed\n",status=500,mimetype="application/json")
    
    #Finding user with the given email address
    user = users.find_one({"email":data['email']})
    #Finding product with given product_id
    product = products.find_one({"product_id":data['product_id']})

    #Checking if user is an admin
    if user['category'] == "admin":
        #Checking if the product with the given id exists
        if product != None:
            #If user's input contains the 'name' key 
            if "name" in data:
                #Updating the product
                products.update_one({"product_id":data['product_id']}, 
                {"$set":
                    {
                        "name":data['name']
                    }
                })
            #If user's input contains the 'price' key 
            if "price" in data:
                #Updating the product
                products.update_one({"product_id":data['product_id']}, 
                {"$set":
                    {
                        "price":data['price']
                    }
                })
            #If user's input contains the 'description' key 
            if "description" in data:
                #Updating the product
                products.update_one({"product_id":data['product_id']}, 
                {"$set":
                    {
                        "description":data['description']
                    }
                })
            #If user's input contains the 'stock' key 
            if "stock" in data:
                #Updating the product
                products.update_one({"product_id":data['product_id']}, 
                {"$set":
                    {
                        "stock":data['stock']
                    }
                })
            #Passing the product's name and the string " was updated" to variable msg
            msg = product['name'] + " was updated\n"
            #Response if query executed successfully
            return Response(msg, status=200, mimetype='application/json')
        #There is no product with the given email
        else:
            #Response if there is no student with the given email
            return Response("No product with that id was found\n", status=500, mimetype='application/json')
    #User's category is not 'admin'
    else:
        #Error response if user is not an admin
        return Response("User is not an admin\n", status=400, mimetype='application/json')  

#flask service, port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)