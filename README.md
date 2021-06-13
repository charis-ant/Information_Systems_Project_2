# Ergasia2_e18011_Charis_Antoniadi
This project is about executing queries for a Mongodb database, using the pymongo module of python. The app2.py file contains thirteen endpoints, each used for the POST, GET, PATCH and DELETE HTTP methods.

## Preparation
Firstly we need to open a terminal window to start docker
```bash
sudo dockerd
```
In a new terminal window, we type the commands bellow
```bash
sudo docker pull mongo #to pull the image from docker hub
sudo docker pull mongo:4.0.4 #to download the latest version of MONGODB image
sudo docker run -d -p 27017:27017 --name mongodb2 mongo:4.0.4 #to deploy image for the first time
sudo docker start mongodb2 #to start mongodb2
```
Then we are going to use the Mongo Shell to create the DSMarket database, which will contain two collections. The fist one is called Users and contains the all the user's info and the second one is called Products and contains all the product's info. To access the mongo shell we type:
```bash
sudo docker exec -it mongodb mongo
```
In Mongo Shell we type:
```bash
use DSMarkets #to create DSMarkets db
```
When we are ready to run the project, we use the command python3 followed by the file name, as seen below

```bash
python3 app2.py
```
*note: If the app2.py file isn't located in the default path, we use the cd command in order to relocate to the directory where the file is located.*

## Execution
### Create User Admin (POST) and Create User Customer
In order to execute all the endpoints, we have to create a users, which will be added to the Users collection. Since there are two categories that a user whould belong to, there also two "Create User" functions/endpoints. The first one is called createUserAdmin and as its name suggest, it is used for the initialization of an admin user in the database. The other function is called createUserCustomer and it is used in order to create a customer user in the database. In order to work, both of the endpoints have to take as input the email, the name and the desired password of the user. To execute the endpoint in a new terminal window we can type one of the commands bellow, depending on the user's category:
```bash
curl -X POST localhost:5000/createUserAdmin -d '{"email":"insert email here", "name":"insert name here", "password":"insert password here"}' -H Content-Type:application/json
```
```bash
curl -X POST localhost:5000/createUserCustomer -d '{"email":"insert email here", "name":"insert name here", "password":"insert password here"}' -H Content-Type:application/json
```
The result if there is no other entry in the collection with the given email, will be a success response as seen in the image bellow
![create user function](create_user.png)
In case the given username already exist, the output will be a corresponding response. Because there are two endpoints dedicated to the creation of a user, depending on their category, the user's category will be added automaticly to the database, based on the name of the endpoint (lines ......of the app2.py file).

### Login (POST)
Now, the user needs to be logged in. This will happen by typing the command:
```bash
curl -X POST localhost:5000/login -d '{"username":"insert username here", "password":"insert password here"}' -H Content-Type:application/json
```
If the login information are correct then a success message followed by the user's session uuid and username will show up
![login function](login.png)

### Get student (GET)
If we want to print the information of a student with a specific email, then in the terminal window we type:
```bash
curl -X GET localhost:5000/getStudent -d '{"email":"insert email here"}' -H "authorization: the user's uuid (printed in the terminal after the successful execution of the login query)" -H Content-Type:application/json
```
The result should look like the image bellow
![get student funtion](get_student.png)
