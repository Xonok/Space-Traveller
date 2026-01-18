This is an open-source project.
If you want to contribute, start by joining our discord and contacting Xonok. (Link in the readme)
Just want to play around? Pull the repo and try running server.py, it requires python 3, any version of that should work.
Then go to localhost and see if it works.
Note that it must be http://localhost, not https://localhost, at least until you get a certificate and turn on SSL.

Configuration:
backend - runs the game on port 9200 only, meaning it won't be visible on the normal HTTP and HTTPS ports(80 and 443 respectively). This is for having a frontend server as a reverse proxy for multiple backend servers, like it does on our official server.
ssl - Enables the HTTPS site, but you need an SSL certificate. Self-signed is fine for personal use. (https://localhost)
saving - Whether the server can change any files in the data folder. I turn this off when I make potentially breaking changes, or when I want to repeatedly test the same situations.
bundle - false, true, "cache". Whether to combine html and JS files so there would be fewer round trips upon first navigating to a page. Off by default because it can silently break.