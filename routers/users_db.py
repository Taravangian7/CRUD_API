#This file allows you to create, update, search and delete users. The database is in MongoDB
from fastapi import APIRouter,HTTPException
from db.models.user import User
from db.schemas.user import user_schema,users_schema
from db.client import db_client
from bson import ObjectId

router=APIRouter()

#Searches the database for a user (filtering by mail) and returns the user in a python user object.
def search_user_by_email(email:str):
    try:
        user=user_schema(db_client.users.find_one({"email":email}))
        return User(**user)
    except:
        return {'error':'User not found'}

#Searches the database for a user (filtering by id) and returns the user in a python user object.
def search_user(id:str):
    try:
        user=user_schema(db_client.users.find_one({"_id":ObjectId(id)})) #ObjectId convert the str id to a MongoDB id
        return User(**user)
    except:
        return {'error':'User not found'}

#I make a request to obtain the list of users.
@router.get('/usersdb',response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

#Requets to get a particular user, searching by id
@router.get("/userdb/{id}")
async def user(id:str):
    return search_user(id)

#Here we can create a new user
@router.post('/usersdb',response_model=User) #"response_model is what we expect to get from this function"
async def user(user:User):
    if type(search_user_by_email(user.email))==User:
        raise HTTPException(status_code=404, detail='User already exists')
    user_dict=dict(user) #I receive User type and transform it into dict to be able to enter it into the MongoDB database.
    del user_dict["id"] #If an id were given, I just delete it
    id = db_client.users.insert_one(user_dict).inserted_id #I enter the user into the database and save the id that is automatically created.
    new_user = user_schema(db_client.users.find_one({"_id":id})) #I get the new user directly from the database. In mongoDB the id is stored under the key "_id".
    return User(**new_user)

#User upload
@router.put('/userdb/',response_model=User)
async def user(user:User):
    try:
        user_dict=dict(user)
        del user_dict['id']
        db_client.users.find_one_and_replace({"_id":ObjectId(user.id)},user_dict)
    except:
        return {'Error':'User cannot be updated'}
    return search_user(user.id)
        
#Delete user:
@router.delete('/userdb/{id}',status_code=200)
async def user(id:str):
    found=db_client.users.find_one_and_delete({"_id":ObjectId(id)})
    print(type(found))
    if not found:
        return {'Error':'This user is not in the database'}
    else:
        return {'Completed':'User deleted succesfully'}