class BaseError(Exception):
	pass
#Not logged in, redirect to login.
class Auth(BaseError):
	pass
#Character not selected. Redirect to characters.
class Char(BaseError):
	pass
#This page is currently invalid, redirect to nav. (F.e, trade page when not on a structure)
class Page(BaseError):
	pass
#Redirect to battle
class Battle(BaseError):
	pass
#Invalid query. Returns error text to user, so they can fix it on their side.
class User(BaseError):
	pass
#Server completed the task successfully, but should return immediately.
class Fine(BaseError):
	pass