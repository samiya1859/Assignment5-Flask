destination_counter = 0


class Destination:
    def __init__(self, name, description, location, admin_email):
        global destination_counter
        destination_counter += 1
        self.id = destination_counter
        self.name = name
        self.description = description
        self.location = location
        self.admin_email = admin_email

    def __repr__(self):
        return f"Destination({self.name}, {self.description}, {self.location}, {self.admin_email})"

    def to_dict(self):
        """
        Convert the Destination object to a dictionary for JSON serialization
        """
        return {
            "id": str(self.id),  # Convert to string to ensure JSON compatibility
            "name": self.name,
            "description": self.description,
            "location": self.location,
            # Optionally include other attributes as needed
        }
