#This file allows you to create, update, search and delete users. The database is in MongoDB and you need authentication. Passwords are encrypted.
from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm #To encrypt the passwords
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta
from db.models.user import User,User2
from db.schemas.user import user_schema,users_schema,user_schema2
from db.client import db_client
from bson import ObjectId

router=APIRouter()
#This is created to be able to do authentication. It is a standard that determines how to work with authentication.
#Once authenticated, you must pass the token type "bearer".
oauth2= OAuth2PasswordBearer(tokenUrl='login2') #This means that I have to send "/login2" to start the authentication operation.

ALGORITHM="HS256"
ACCESS_TOKEN_DURATION=5 #Time we are authenticated with the token
SECRET="eltonketa" 
crypt=CryptContext(schemes=["bcrypt"])

#Searches the database for a user (filtering by username) and returns the user in a python user object. It don't bring the password.
def search_user_by_username(username:str):
    try:
        user=user_schema(db_client.users2.find_one({"username":username}))
        return User(**user)
    except:
        return {'error':'User not found'}

#Searches the database for a user (filtering by id) and returns the user in a python user object. It don't bring the password.
def search_user(id:str):
    try:
        user=user_schema(db_client.users2.find_one({"_id":ObjectId(id)})) #ObjectId convert the str id to a MongoDB id
        return User(**user)
    except:
        raise HTTPException(status_code=401,detail='User not found')

#This function receives the authentication token and, if valid, returns the associated user.
#This function has as parameter a token, which is obtained when the authenticating is made. This token is obtained from Oauth2 defined above.
async def oauth_user(token:str =Depends(oauth2)):
    exception= HTTPException(status_code=401,detail='Invalid authentication credentials')
    try:
        id= jwt.decode(token,SECRET,algorithms=[ALGORITHM]).get('sub') #Using the token obtained after authentication,
        #the "secret" variable I defined earlier and the encryption algorithm, I get the id. The id is obtained by doing ".get("sub")", becouse "access_token" is a dictonary
        if id is None: #means you can't obtain anything using this token.
            raise exception
    except:
        raise exception
    return search_user(id)

#This function has the purpose of filter the inactive users.
#This function has a dependence with "oauth_user" function, it recieves its output.
async def current_user(user: User=Depends(oauth_user)):
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Inactive user') 
    return user

#Here we can create a new user. User don't need to be aunthenticated to do this.
@router.post('/users2db',response_model=User) #"response_model is what we expect to get from this function"
async def user(user:User2):
    if type(search_user_by_username(user.username))==User:
        raise HTTPException(status_code=404, detail='User already exists')
    user_dict=dict(user) #I receive User type and transform it into dict to be able to enter it into the MongoDB database.
    del user_dict["id"] #If an id were given, I just delete it
    user_dict["password"]=crypt.encrypt(user_dict["password"]) #The password is stored encrypted.
    id = db_client.users2.insert_one(user_dict).inserted_id #I enter the user into the database and save the id that is automatically created.
    new_user = user_schema(db_client.users2.find_one({"_id":id})) #I get the new user directly from the database. In mongoDB the id is stored under the key "_id".
    return User(**new_user)

#AUTHENTICATION OPERATION
@router.post('/login2') #This address has to be the one you put in the tokenurl (above)
async def login(form:OAuth2PasswordRequestForm = Depends()): #This function uses a form parameter. "form" allows us to reference a username and a password.
    #depends on the data we pass in postman (this data in form type)
    exception=HTTPException(status_code=400,detail='User is not correct')
    try:
        user=User2(**user_schema2(db_client.users2.find_one({"username":form.username}))) #If the username exist, I get the user (UserDB class)
    except:
        raise exception
    if not crypt.verify(form.password,user.password):  #form.password is the password we have received. Verify decrypts the one we have stored in the database and compares it with the one entered.
        raise HTTPException(status_code=400,detail='Password is not correct')
    print(user.password)
    access_token={'sub':user.id,
                  'exp':datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_DURATION)}
    return {'access_token':jwt.encode(access_token,SECRET,algorithm=ALGORITHM),'token_type':'bearer'} #We have to return an access token, it should be encrypted. 
    #The token has the purpose of not being continuously authenticating with the server.

#I make a request to obtain the list of users. Have to be authenticathed.
@router.get('/users2db',response_model=list[User])
async def users(user:User =Depends(current_user)):
    return users_schema(db_client.users2.find())

#Requets to get a particular user, searching by id. Have to be authenticathed.
@router.get("/user2db/{id}")
async def user(id:str,user:User =Depends(current_user)):
    return search_user(id)

#User upload. An user should only can do it with itself. Have to be authenticathed.
@router.put('/user2db/',response_model=User)
async def user(user_updated:User2,user_original:User=Depends(current_user)):
    try:
        user_dict=dict(user_updated)
        del user_dict['id']
        user_dict["password"]=crypt.encrypt(user_dict["password"]) #The password is stored encrypted.
        db_client.users2.find_one_and_replace({"_id":ObjectId(user_original.id)},user_dict)
    except:
        return {'Error':'User cannot be updated'}
    return search_user(user_original.id)
        
#Delete user. An user should only can do it with itself. Have to be authenticathed.
@router.delete('/user2db',status_code=200)
async def user(user:User =Depends(current_user)):
    try:
        db_client.users2.find_one_and_delete({"_id":ObjectId(user.id)})
        return {'Completed':'User deleted succesfully'}
    except:
        raise HTTPException(status_code=400,detail='User was already deleted')

#Delete all the database. Have to know the SECRET str (The method is not safe at all, it should be improved.)
@router.delete('/user2db/del',status_code=200)
async def user():
        db_client.users2.delete_many({})
        return {'Completed':'Database deleted succesfully'}