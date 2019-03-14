class Medicine(object):
    def __init__(self, name, form, dosage,
                 ttl=180, produced_time=0, price=100):
        self.name = name
        self.form = form
        self.dosage = dosage
        self.ttl = ttl
        self.produced_time = produced_time
        self.price = price
    
    def name(self):
        return '_'.join([str(self.name), str(self.form), str(self.dosage)])
    
    def __eq__(self, other):
        return self.name() == other.name()# and self.is_discounted() == other.is_discounted()
    
    def is_discounted(self):
        return self.ttl < 30
    
    def pass_days(self, days=1):
        self.ttl -= days
        return self
