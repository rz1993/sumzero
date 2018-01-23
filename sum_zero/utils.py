MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
    'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def pretty_date(date_obj):
    return "{} {}".format(MONTHS[date_obj.month-1], date_obj.day)

def paginate(queryset=None):
    return None
