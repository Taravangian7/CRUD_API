#Main file, includes different routers.
from fastapi import FastAPI
from routers import users,jwt,users_db,users_db2

#http://127.0.0.1:8000
app=FastAPI()
app.include_router(users.router) #VERSION 1: database as a python list of users. CRUD
app.include_router(jwt.router) #VERSION 2: database as a python dict of users, includes encrypted password. Login and read (if user is allowed).
app.include_router(users_db.router)#VERSION 3: using a mongoDB database, could be remote or local. CRUD
app.include_router(users_db2.router) #VERSION 4: CRUD.MongoDB database, could be remote or local. Includes encrypted password, login aunthentication and enabled/disables users.

@app.get('/')
async def root():
    return 'Hello world, this is an API test'

@app.get('/url')
async def url():
    return {'my_url':'https://github.com/Taravangian7'}