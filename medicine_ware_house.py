MIN_COST, MAX_COST = 100, 10000
REQUEST_NUM = 30


class Stock(object):
    def __init__(self, elements_set):
        self.elements_set = elements_set
        self.stock = []
        self.quantity = dict([(x.name(), 0) for x in elements_set])
    
    def decrease_ttl(self):
        for i in range(len(self.stock)):
            self.stock[i].ttl -= 1
    
    def get_quantity(self, element):
        return self.quantity[element.name()]
    
    def get_elements_set(self):
        return [tuple(x.name().split('_')) for x in self.elements_set]
    
    def get_available_elements(self):
        result = set([elem for elem, count in self.quantity.items() if count > 0])
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
        super(self, SortedStock).__init__(elements_set)
    
    def clear(self):
        to_del = [x for x in self.stock if x.ttl == 0]
        self.stock = self.stock[len(to_del):]
        for x in to_del:
            self.quantity[x.name] -= 1
    
    def add_element(self, element, quantity=1):
        assert element in self.elements_set, print(f'{element.name()} is unknown to this stock')
        
        self.stock = sorted(self.stock + [element] * quantity, key=lambda x: x.ttl)
        self.quantity[element.name()] += quantity
    
    def add_elements(self, elements):
        assert all([x in self.elements_set for x in elements]), print(f'encountered unknown element')
        
        self.stock = sorted(self.stock + elements, key=lambda x: x.ttl)
        for x in elements:
            self.quantity[x.name()] += 1
    
    def extract_element(self, element, quantity=1):
        result = [x for x in self.stock if x == element][:quantity]
        self.stock = self.stock[len(result):]
        for x in result:
            self.quantity[x.name()] -= 1
        return result, quantity - (quantity - len(result))
    
    def extract_elements(self, elements):
        return [self.extract_element(x, quantity=1) for x in elements]
    
    def get_top(self, top):
        result = self.stock[:top]
        self.stock = self.stock[top:]
        for x in result:
            self.quantity[x.name()] -= 1
        return result


class MedicineWareHouse(object):
    def __init__(self, medicines_set, min_instances=5):
        medicines_set = set(medicines_set)
        self.medicines_set = medicines_set
        self.stock = SortedStock(elements_set=medicines_set)
        self.sale_stock = SortedStock(elements_set=medicines_set)
        self.min_instances = min_instances
        self.quantity = dict((x.name(), 0) for x in medicines_set)
        self.medicines_to_request = dict((x.name(), False) for x in medicines_set)
    
    def get_medicines_set(self):
        return self.stock.get_elements_set()
    
    def get_available_medicines(self):
        return self.stock.get_available_elements(), self.sale_stock.get_available_elements()
    
    def move_to_sale(self):
        to_move = len([x for x in self.stock.get_ttl() if x.ttl < 31])
        self.sale_stock.add_elements(self.stock.get_top(top=to_move))
    
    def add_medicine(self, medicine, quantity=1):
        self.stock.add_elements([medicine] * quantity)
        self.update_quantity()
    
    def get_medicine(self, medicine, quantity=1, is_sale=True):
        medicine = [x for x in self.medicines_set if self.medicine_equality(x, medicine)]
        if is_sale:
            result = self.sale_stock.extract_element(element=medicine, quantity=quantity)
        else:
            result = self.stock.extract_element(element=medicine, quantity=quantity)
        self.update_quantity()
        return result[0], result[1]
    
    def update_quantity(self):
        stock_quantity = self.stock.get_quantity()
        sale_quantity = self.sale_stock.get_quantity()
        for x in self.quantity:
            quantity = stock_quantity[x] + sale_quantity[x]
            self.quantity[x] = quantity
            if quantity < self.min_instances:
                self.medicines_to_request[x] = self.costs[x] * REQUEST_NUM
            else:
                self.medicines_to_request[x] = 0
    
    def goto_next_day(self):
        self.stock.decrease_ttl()
        self.sale_stock.decrease_ttl()
        self.stock.clear()
        self.sale_stock.clear()
        self.move_to_sale()
        self.update_quantity()
    
    def required_medicines(self):
        return [x for x, v in self.medicines_to_request.items() if v]
    
    def medicine_equality(self, medicine, order):
        eq = medicine.name == order.name
        if (order.form is None) and (order.dosage is not None):
            eq = eq and (medicine.dosage == order.dosage)
        elif (order.form is not None) and (order.dosage is None):
            eq = eq and (medicine.form == order.form)
        else:
            eq = medicine.name() == order.name()
        return eq


class OrderList(object):
    def __init__(self, phone_number, address, order_list, discount_id=None):
        self.phone_number = phone_number
        self.address = address
        self.order_list = order_list
        self.discount_id = discount_id