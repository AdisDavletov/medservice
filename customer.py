class Customer(object):
    def __init__(self, name, address,
                 phone_number, discount_id=None):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.discount_id = discount_id
    
    def id(self):
        return '_'.join([str(self.name), str(self.address), str(self.phone_number)])
    
    def __eq__(self, other):
        return self.id() == other.id()
