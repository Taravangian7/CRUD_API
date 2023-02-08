# CRUD_API
Development of API
In this project an API is developed to create, read, update and delete users. 
There are different versions, which can be found in the main file. The best version allows to use a mongoDB database, where the users are stored. 
The password of the users is stored encrypted. 
In addition, users must authenticate to access certain functions. When they authenticate, they get a token that allows them to make requests. 
Finally, users can be enabled or disabled, in the latter case they will not be able to access the functions even if they authenticate, as they will not be authorized.
