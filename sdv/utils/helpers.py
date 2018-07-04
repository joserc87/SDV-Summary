import string
import random


def random_id(length=6):
    chartacter_pool = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.sample(chartacter_pool, length))
