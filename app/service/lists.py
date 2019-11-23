def get_lists(current_user, offset=0, limit=None, start_today=False):
    lists = current_user.get_lists()
    obj = [l.to_dict(offset, limit, start_today) for l in lists]
    return obj
