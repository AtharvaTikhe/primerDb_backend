import uuid

def create_uuid(seq_id):
    id = str(uuid.uuid4())
    id += '-'
    id += seq_id

    return id


