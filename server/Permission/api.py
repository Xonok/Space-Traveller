from server import defs

def check(cname,tstruct,permission):
	if tstruct["owner"] == cname:
		return True
	group = defs.group_of.get(cname)
	if not group:
		return False
	rank = group["member_rank"].get(cname)
	if not rank:
		return False
	props = tstruct["props"]
	req = props.get("permission",{}).get(permission)
	ranks = group["ranks"]
	if not req or req not in ranks or rank not in ranks:
		return False
	rank_idx = ranks.index(rank)
	req_idx = ranks.index(req)
	if req_idx < rank_idx:
		return False
	return True