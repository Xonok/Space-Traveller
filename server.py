#WEB LOGIC
#Respond to get requests for any file in the css, img or js folders.
#Get requests to other folders should return 403(permission denied), except html in main folder.
#Respond to blank request by redirecting to login screen.

#GAME LOGIC(requests)
#Login and register. Keep track of users on disk and in memory.
#Every request requires a session ID. Redirect to login if missing or invalid.
#Requests needed:
#Register/Login - username+password hashed. Return session key if successful, 401 if not.
#Move - session key + coordinates
#Dock - session key + coordinates
#Trade - session key + coordinates + buy dict + sell dict, these dicts are name: amount. Ignore invalid values.
#For Dock and Trade, check location. If no buildings, give "no buildings" page.

#GAME LOGIC(async)
#Every day at 4AM do these things:
#Increase resources on tiles that are not full, up to limit.
#Tick buildings. First calculate if tick can be done, then remove resources, then add.
#If not enough space, throw away cheapest resources first, of those produced this tick.
