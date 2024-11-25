import uuid

class Destination:
    def __init__(self, name, description, location, admin_email):
        self.id = str(uuid.uuid4())  # Generate a unique ID
        self.name = name
        self.description = description
        self.location = location
        self.admin_email = admin_email 

    def __repr__(self):
       return f"Destination({self.name}, {self.description}, {self.location}, {self.price}, {self.admin_email})"

# In-memory storage for destinations
destinations = {}