from app.api.exceptions import APIError


def extract_args(args):
    offset = int(args.get("offset")) if "offset" in args else 0
    if (offset and offset > 5000) or (offset and offset < -5000):
        raise APIError("Offset needs to be within -5000 and 5000")
    limit = int(args.get("limit")) if "limit" in args else None
    if limit and limit > 25:
        raise APIError("Limit cannot be over 25")
    start_today = (
        bool(args.get("start_today")) if "start_today" in args else False
    )
    return dict(offset=offset, limit=limit, start_today=start_today)
