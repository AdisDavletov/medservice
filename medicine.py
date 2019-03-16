class Medicine(object):
    def __init__(self, name, form, dosage,
                 ttl=180, produced_time=0):
        self.name = name
        self.form = form
        self.dosage = dosage
        self.ttl = ttl
        self.produced_time = produced_time
    
    def name(self):
        return '_'.join([str(self.name), str(self.form), str(self.dosage)])
    
    def __eq__(self, other):
        return self.name() == other.name()