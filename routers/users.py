#This file allows you to create, update, search and delete users by simulating the database as a python list.
from fastapi import APIRouter
from pydantic import BaseModel #Use BaseModel to avoid the "__init__" constructor when you create a class

router=APIRouter()

class User(BaseModel):
    id:int
    name:str
    surname:str
    age:int

#This list is being used as data base (only for this file).
user_list=[User(id=1,name='Taravangian',surname='Mantra',age=29),
           User(id=2,name='Heros',surname='Elaña',age=2)]

#This function takes as a parameter an "id" and returns the user associated with it.
def search_user(id:int):
    users=filter(lambda user: user.id==id,user_list)
    try:
        return list(users)[0]
    except:
        return {'Error':'User not found'}

#This request returns a list with all users.
@router.get('/users')
async def users():
    return user_list

#This request returns an specific user, searching by id.
@router.get("/user/{id}")
async def user(id:int):
    return search_user(id)

#Here we can create a new user, this function needs an User type as parameter. Returns the new user.
@router.post('/users/')
async def user(user:User):
    if type(search_user(user.id))==User:
        return {'Error':'this user already exists'}
    else:
        user_list.append(user)
        return user

#Here we can update an user, this function needs an User type as parameter. Returns the updated user.
@router.put('/user/')
async def user(user:User):
    found=False
    for index,saved_user in enumerate(user_list):
        if saved_user.id==user.id:
            user_list[index]=user
            found=True
            return user
    if not found:
        return {'Error':'The user could not be updated'}

#Here we can delete an user, this function needs an id (int) as parameter.
@router.delete('/user/{id}')
async def user(id:int):
    found=False
    for index,saved_user in enumerate(user_list):
        if saved_user.id==id:
            del user_list[index]
            found=True
    if not found:
        return {'Error':'The user could not be deleted'}


    

