# The Main Points

This is an open-source project.
If you want to contribute, start by joining our discord and contacting Xonok. (Link in the readme)
Just want to play around? Pull the repo and try running server.py, it requires python 3, any version of that should work.
Then go to localhost and see if it works.
Note that it must be http://localhost, not https://localhost, unless you get a certificate and turn on https.

## Configuration

_logging_ - currently unused
_saving_ - if false, the server avoids saving anything into /data. Useful for testing risky changes, or repeatedly starting from the same state for debugging.
_bundle_ - whether to compile the html and js files together. Disabled until we switch to a more reasonable bundler library.
_http\_port_ - which port to run the game on
_https\_port_ - which port to run the game on, but with SSL enabled. If this is on, http_port redirects to this instead of serving clients directly. If this is null, the https port is disabled(default).
_interactive_ - whether the server expects to be run with the -i python flag, thus enabling you to touch server internals while it's running. Default is true. **If the server randomly stops the moment you start it, this is why**. Either do "python3 -i server.py" or turn this off.

The launcher script assumes ipython3, not ordinary python3, because it deals better with writing commands while the log is moving.

## Why doesn't the server respond at all when I go to localhost?

Your browser might have switched the site to https while you weren't looking.
Switch it back to http by changing the url in your browser.
If it keeps switching to https, you'll have to adjust your browser settings or enable a https port in the server config.

## How to enable HTTPS?

First you need to generate an SSL certificate. OpenSSL is a good choice.
You'll need to install it first, then:
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365
This will ask you several questions and in the end will produce 2 files, which you need to put into .ssh in traveller. 
You'll also need to enable a https port by changing the server config. Set the https port to 443 - it's what browsers expect. All other options are for those who don't need me to tell them what to do.
A handmade cert like this is not trusted by browsers and will provoke warnings, but is convenient for a beginner.
If your browser rejects the site due to this kind of certificate and doesn't let you do it anyway, then you can use a better browser that has more trust in your intelligence. Something like Firefox perhaps.
