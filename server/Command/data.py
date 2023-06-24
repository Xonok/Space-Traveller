from server import map
from . import procedure,query

procedure.command("move",map.move3)
procedure.bind("move","vision","tiles","tile","cdata","ships","buttons","structure","idata","hwr","constellation","ship_defs","starmap","messages")

procedure.query("vision",query.get_vision)
procedure.query("tiles",query.tiles)
procedure.query("tile",query.tile)
procedure.query("cdata",query.cdata)
procedure.query("ships",query.active_ships)
procedure.query("buttons",query.buttons)
procedure.query("structure",query.get_structure)
procedure.query("idata",query.idata)
procedure.query("hwr",query.hwr)
procedure.query("constellation",query.constellation)
procedure.query("ship_defs",query.ship_defs)
procedure.query("starmap",query.starmap)
procedure.query("messages",query.messages)