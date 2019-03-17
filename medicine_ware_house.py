from random import randint


class Stock(object):
    def __init__(self, elements_set):
        self.elements_set = elements_set
        self.stock = []
    
    def decrease_ttl(self):
        for i in range(len(self.stock)):
            self.stock[i].ttl -= 1
    
    def get_element_quantities(self, element):
        return self.get_quantities()[element.id()]
    
    def get_quantities(self):
        quantities = dict([(x.id(), 0) for x in self.elements_set])
        for x in self.stock:
            quantities[x.id()] += 1
        return quantities
    
    def get_elements_set(self):
        return [x for x in self.elements_set]
    
    def get_available_elements(self):
        quantities = self.get_quantities()
        result = set([elem for elem, count in quantities.items() if count > 0])
        return result
    
    def apply(self, func):
        return [func(x) for x in self.stock]
    
    def get_ttl(self):
        return [x.ttl for x in self.stock]
    
    def add_element(self, element, quantity):
        raise NotImplementedError()
    
    def add_elements(self, elements):
        raise NotImplementedError()
    
    def extract_element(self, element, quantity):
        raise NotImplementedError()
    
    def clear(self):
        raise NotImplementedError()


class SortedStock(Stock):
    def __init__(self, elements_set):
        super().__init__(elements_set)
        self.quantities = dict([(x.id(), 0) for x in elements_set])
    
    def clear(self):
        to_del = len([x for x in self.stock if x.ttl <= 0])
        [self.stock.pop(0) for _ in range(to_del)]
        self.quantities = self.get_quantities()
    
    def add_element(self, element, quantity=1):
        assert element in self.elements_set, print(f'{element.id()} is unknown to this stock')
        
        self.stock = sorted(self.stock + [element] * quantity, key=lambda x: x.ttl)
        self.quantities = self.get_quantities()
    
    def add_elements(self, elements):
        assert all([x in self.elements_set for x in elements]), print(f'encountered unknown element')
        
        self.stock = sorted(self.stock + elements, key=lambda x: x.ttl)
        self.quantities = self.get_quantities()
    
    def extract_element(self, element, quantity=1):
        result = [i for i, x in enumerate(self.stock) if x == element][:quantity]
        result = [self.stock.pop(result[0]) for _ in result]
        self.quantities = self.get_quantities()
        return result, quantity - (quantity - len(result))
    
    def extract_elements(self, elements):
        result = [self.extract_element(x, quantity=1) for x in elements]
        self.quantities = self.get_quantities()
        return result
    
    def get_top(self, top):
        result = [self.stock.pop(0) for i in range(top)]
        self.quantities = self.get_quantities()
        return result


class MedicineWareHouse(object):
    def __init__(self, medicines_set, min_instances=5):
        medicines_set = set(medicines_set)
        self.medicines_set = medicines_set
        self.stock = SortedStock(elements_set=medicines_set)
        self.sale_stock = SortedStock(elements_set=medicines_set)
        self.min_instances = min_instances
        self.quantities = dict((x.id(), 0) for x in medicines_set)
        self.medicines_to_request = dict((x.id(), False) for x in medicines_set)
    
    def get_medicines_set(self):
        return self.stock.get_elements_set()
    
    def get_available_medicines(self):
        return self.stock.get_available_elements(), self.sale_stock.get_available_elements()
    
    def move_to_sale(self):
        to_move = len([x for x in self.stock.get_ttl() if x < 31])
        self.sale_stock.add_elements(self.stock.get_top(top=to_move))
    
    def add_medicine(self, medicine, quantity=1):
        self.stock.add_elements([medicine] * quantity)
    
    def get_medicine(self, medicine, quantity=1, is_sale=True):
        if isinstance(medicine, str):
            name, form, dosage = medicine.split('_')
            form = None if form == 'None' else form
            dosage = None if dosage == 'None' else dosage
            medicine = Medicine(name, form, dosage)
        
        medicines = [x for x in self.medicines_set if self.medicine_equality(x, medicine)]
        if len(medicines) == 0:
            return [], 0
        res_quantity = 0
        result = []
        while res_quantity != quantity and len(medicines) > 0:
            idx = randint(0, len(medicines) - 1)
            medicine = medicines.pop(idx)
            new_quantity = quantity - res_quantity
            if is_sale:
                new_result = self.sale_stock.extract_element(element=medicine, quantity=new_quantity)
            else:
                new_result = self.stock.extract_element(element=medicine, quantity=new_quantity)
            result.extend(new_result[0])
            res_quantity += new_result[1]
        
        return result, quantity - (quantity - res_quantity)
    
    def update_quantities(self):
        stock_quantities = self.stock.get_quantities()
        sale_quantities = self.sale_stock.get_quantities()
        for x in self.quantities:
            self.quantities[x] = stock_quantities[x] + sale_quantities[x]
            if self.quantities[x] < self.min_instances:
                self.medicines_to_request[x] = True
            else:
                self.medicines_to_request[x] = False
        return self.quantities
    
    def goto_next_day(self):
        self.stock.decrease_ttl()
        self.sale_stock.decrease_ttl()
        self.stock.clear()
        self.sale_stock.clear()
        self.move_to_sale()
        self.update_quantities()
    
    def required_medicines(self):
        return [x for x, v in self.medicines_to_request.items() if v]
    
    def medicine_equality(self, medicine, other):
        eq = medicine.name == other.name
        if eq and (other.form is None) and (other.dosage is not None):
            eq = eq and (medicine.dosage == other.dosage)
        elif eq and (other.form is not None) and (other.dosage is None):
            eq = eq and (medicine.form == other.form)
        elif (other.form is None) and (other.dosage is None):
            eq = eq
        else:
            eq = medicine.id() == other.id()
        return eq
    
    def get_quantities(self):
        self.update_quantities()
        return self.quantities


class Medicine(object):
    def __init__(self, name, form, dosage,
                 ttl=180, produced_time=0):
        self.name = name
        self.form = form
        self.dosage = dosage
        self.ttl = ttl
        self.produced_time = produced_time
    
    def id(self):
        return '_'.join([str(self.name), str(self.form), str(self.dosage)])
    
    def __eq__(self, other):
        return self.id() == other.id()
    
    def __hash__(self):
        return str.__hash__(self.id())
    
    def change(self, **kwargs):
        for key, value in kwargs:
            setattr(self, key, value)
        return self
    
    def __repr__(self):
        return self.id()


class Order(object):
    def __init__(self, phone_number, address, order, discount_id=None, is_sale=True, regular=False):
        self.phone_number = phone_number
        self.address = address
        self.order = order
        self.discount_id = discount_id
        self.is_sale = is_sale
        self.regular = regular
    
    def __repr__(self):
        return str(self.order)
    
    def id(self):
        return '_'.join([self.phone_number, self.address])


if __name__ == '__main__':
    whouse = MedicineWareHouse(
        [Medicine('d', 't', 1), Medicine('d', 'k', 1), Medicine('s', 't', 1), Medicine('d', 't', 1)])
    whouse.add_medicine(Medicine('d', 't', 1), 20)
    whouse.add_medicine(Medicine('d', 'k', 1), 20)
    whouse.add_medicine(Medicine('s', 't', 1), 20)
    whouse.add_medicine(Medicine('d', 't', 1), 20)
    res = whouse.get_medicine(Medicine('d', 't', 1), 44, is_sale=False)
