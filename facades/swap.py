from actions.swap import create_swap_task, get_swap_task

def add_swap_task(payload):
    return create_swap_task(payload)

def fetch_swap_task(id):
    return get_swap_task(id)
