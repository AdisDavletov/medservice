from medicin import Medicine


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
        return [tuple(x.name().split()) for x in self.elements_set]
    
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
    
    def move_to_sale(self):
        to_move = len([x for x in self.stock.get_ttl() if x.ttl < 31])
        self.sale_stock.add_elements(self.stock.get_top(top=to_move))
    
    def add_medicine(self, medicine, quantity=1):
        self.stock.add_elements([medicine] * quantity)
        self.update_quantity()
    
    def get_medicine(self, medicine, quantity=1, is_sale=True):
        if is_sale:
            result = self.sale_stock.extract_element(element=medicine, quantity=quantity)
        else:
            result = self.stock.extract_element(element=medicine, quantity=quantity)
        self.update_quantity()
        return result
    
    def update_quantity(self):
        stock_quantity = self.stock.get_quantity()
        sale_quantity = self.sale_stock.get_quantity()
        for x in self.quantity:
            quantity = stock_quantity[x] + sale_quantity[x]
            self.quantity[x] = quantity
            if quantity < self.min_instances:
                self.medicines_to_request[x] = True
            else:
                self.medicines_to_request[x] = False
    
    def goto_next_day(self):
        self.stock.decrease_ttl()
        self.sale_stock.decrease_ttl()
        self.stock.clear()
        self.sale_stock.clear()
        self.update_quantity()
        
    def required_medicines(self):
        return [x for x, v in self.medicines_to_request.items() if v]
    
    # def calculate_quantity(self):
    #     quantity = {}
    #     for medicine in self.medicines:
    #         quantity[medicine.id()] = \
    #             len([x for x in self.stock if x == medicine])
    #     return quantity
    #
    # def sanity_check(self):
    #     assert all([(x.form is not None) and (x.dosage is not None) for x in self.medicines])
    #     assert all([medicine in self.medicines for medicine in self.stock])
    #
    # def add_medicines(self, medicines):
    #     assert all([(x.form is not None) and (x.dosage is not None) for x in medicines])
    #     self.stock.extend(medicines)
    #
    # def get_medicines(self, order_list):
    #     assert all([order.name in [x.name for x in self.medicines] for order, _ in order_list])
    #
    #     def medicine_equality(medicine, order):
    #         eq = medicine.name == order.name
    #         if (order.form is None) and (order.dosage is not None):
    #             eq = eq and (medicine.dosage == order.dosage)
    #         elif (order.form is not None) and (order.dosage is None):
    #             eq = eq and (medicine.form == order.form)
    #         else:
    #             eq = medicine.id() == order.id()
    #         return eq
    #
    #     medicines = []
    #     for order, quantity in order_list:
    #         filtered = [i for i, medicine in enumerate(self.stock) if medicine_equality(medicine, order)]
    #         filtered = sorted(filtered, key=lambda x: x.ttl)
    #         filtered = filtered[:quantity]
    #         extracted = [self.stock.pop(i) for i in filtered]
    #         medicines.append((extracted[0], quantity - (quantity - len(extracted))))
    #
    #     self.quantity = self.calculate_quantity()
    #     return medicines
    #
    # def utilize_old_medicines(self):
    #     self.stock = [medicine for medicine in self.stock if medicine.ttl == 0]
    #     self.quantity = self.calculate_quantity()
    #
    # def get_medicine_by_id_1(self, id_):
    #     name, form, dosage = id_.split('_')
    #     return [x for x in self.medicines if x == Medicine(name, form, dosage)][0]
    #
    # def get_medicine_by_id_2(self, id_):
    #     medicine = None
    #     name, form, dosage = id_.split('_')
    #     filtered = [(i, x) for i, x in enumerate(self.stock) if x == Medicine(name, form, dosage)]
    #     if len(filtered) >= 0:
    #         medicine = self.stock.pop(filtered[0][0])
    #         self.quantity[id_] -= 1
    #     return medicine


class OrderList(object):
    def __init__(self, phone_number, address, order_list, discount_id=None):
        self.phone_number = phone_number
        self.address = address
        self.order_list = order_list
        self.discount_id = discount_id
