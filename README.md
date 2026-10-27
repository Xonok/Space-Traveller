# Space Traveller

Explore the universe, but do it your own way.

Precursors, or "Humans" as they called themselves, disappeared millennia ago, but their creations are still found all across the universe.
Some of those creations are strange devices, the purposes of which we don't know, others are entire races of living beings.
The Hive is one such race. Unlike the other races in the universe, they've been engineered to be in perfect harmony with their own kind.
Still, each Hiveling is an individual and you are one of them.

Choose your own path. Explore the universe, trade with planets and stations, mine resources, do quests, investigate the secrets of the past.
Whatever you choose to do, we want to support you.
Make one character or 20, no problem.
Customize them with skills, get them ships and equipment, heck, even give them their own lore if you so desire.

Want to play? Here's the link to the live server: https://traveller.mallesne.ee/main.html

## Development

All the content is handmade, we've never used a game engine or even a framework for this game.
We don't use any AI for generating pictures either.
This is an open-source project, so anyone can contribute and all the assets are available for your own use, as long as you credit us for making them.

Want to contact us, hang around and chat, or help develop the game? Join our discord: https://discord.gg/f94rMVtz9D

## How to run this?

Make sure you have a version of Python 3 installed.
Clone and install XLib: https://github.com/Xonok/XLib
XLib is a collection of libraries from us;
install instructions are in its own repository.

When XLib is installed, the server should be runnable.
On Windows open cmd in the Space-Traveller folder and do:
python -i server.py
On Linux, use a terminal and do:
python3 -i server.py

Then in your browser go to:
http://localhost

Traveller uses port 80 by default. If you don't like that, change the config. Make sure you run the server at least once before doing that, as that creates the initial config.
Linux in particular doesn't allow using port 80 by default. I solved it by disabling that rule on my machine, you can either do that or change the config(/config/server.json) to use a port above 1023, such as 8080.
If you change the port to 8080 for example, the browser URL becomes:
http://localhost:8080

## Status

The project has been in slow-motion since February 2026 due to lack of time to work on it.
Commits will still trickle in, but slower.
What would speed it up is the ongoing migration finishing.
What would also help is someone taking over parts of the project, for example to add images to items that are missing them, or to develop new content.
Contact us if you want to help. The best way to do that is discord: https://discord.gg/f94rMVtz9D
