#This file allows you to login with username/password and search your user, the database as a python dict.
#Includes encrypted password and a "enabled/disabled" account filter.
from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel #To create the "User" class
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm #To encrypt the passwords
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta

router=APIRouter()

#This is created to be able to do authentication. It is a standard that determines how to work with authentication.
#Once authenticated, you must pass the token type "bearer".
oauth2= OAuth2PasswordBearer(tokenUrl='login') #This means that I have to send "/login" to start the authentication operation.

ALGORITHM="HS256"
ACCESS_TOKEN_DURATION=3 #Time we are authenticated with the token
SECRET="eltonketa" 
crypt=CryptContext(schemes=["bcrypt"])

#This entity travels through the network, so it does not have a password.
class User(BaseModel):
      username: str
      fullname:str
      email:str
      disabled: bool

#Class representing the database user. Here we store the encrypted password.
class UserDB(User):
    password:str

users_db= {
    'Mantra': {
        'username': 'Mantra',
        'fullname':'Taravangian Mantra',
        'email':'taravangian@gmail.com',
        'disabled': False,
        'password':'$2a$12$jNaju/9b8gK/NiMnVkGJ3ubqFm9Uv8wpBoWutpsZpgvjK9Jna8eaW' #This data is encrypted (bcrypt and HS256). Password:123456
    },
    'Berunio': {
        'username': 'Berunio',
        'fullname':'Berunio Oxemburg',
        'email':'latorreste@gmail.com',
        'disabled': True,
        'password':'$2a$12$tB.JfDJHIItUBjRqZ7VzpONa3WXi4A5m1o0DsSaNBCrXF3mRpKuiW'
    }}

def search_user_db(username:str):
    if username in users_db:
        return UserDB(**users_db[username])

def search_user(username:str):
    if username in users_db:
        return User(**users_db[username])

#This function receives the authentication token and, if valid, returns the associated user.
#This function has as parameter a token, which is obtained when the authenticating is made. This token is obtained from Oauth2 defined above.
async def oauth_user(token:str =Depends(oauth2)):
    exception= HTTPException(status_code=401,detail='Invalid authentication credentials')
    try:
        username= jwt.decode(token,SECRET,algorithms=[ALGORITHM]).get('sub') #Using the token obtained after authentication,
        #the "secret" variable I defined earlier and the encryption algorithm, I get the username. The username is obtained by doing ".get("sub")", becouse "access_token" is a dictonary
        if username is None: #means you can't obtain anything using this token.
            raise exception
    except JWTError:
        raise exception
    return search_user(username)

#This function has the purpose of filter the inactive users.
#This function has a dependence with "oauth_user" function, it recieves its output.
async def current_user(user: User=Depends(oauth_user)):
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Inactive user') 
    return user

#AUTHENTICATION OPERATION
@router.post('/login') #This address has to be the one you put in the tokenurl (above)
async def login(form:OAuth2PasswordRequestForm = Depends()): #This function uses a form parameter. "form" allows us to reference a username and a password.
    #depends on the data we pass in postman (this data in form type)
    user_db= users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400,detail='User is not correct')
    user=search_user_db(form.username) #If the username exist, I get the user (UserDB class)
    if not crypt.verify(form.password,user.password):  #form.password is the password we have received. Verify decrypts the one we have stored in the database and compares it with the one entered.
        raise HTTPException(status_code=400,detail='Password is not correct')
    access_token={'sub':user.username,
                  'exp':datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_DURATION)}
    return {'access_token':jwt.encode(access_token,SECRET,algorithm=ALGORITHM),'token_type':'bearer'} #We have to return an access token, it should be encrypted. 
    #The token has the purpose of not being continuously authenticating with the server.


@router.get('/users/me')
async def me(user:User =Depends(current_user)):
    return user