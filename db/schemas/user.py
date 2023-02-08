#This function receives a user from the MongoDB database, and transforms it into a dict.
def user_schema(user)->dict:
    return {"id": str(user["_id"]),
    "username":user["username"],
    "email":user["email"],
    "disabled":user["disabled"]}

#This function is for users_db2.Contains password.
def user_schema2(user)->dict:
    return {"id": str(user["_id"]),
    "username":user["username"],
    "email":user["email"],
    "disabled":user["disabled"],
    "password":user["password"]}

def users_schema (users)->list:
    return [user_schema(user) for user in users]