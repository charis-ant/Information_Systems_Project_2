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
###
