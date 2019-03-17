from collections import defaultdict
from random import randint, sample, shuffle

from delivery_service import DeliveryService
from medicine_ware_house import MedicineWareHouse, Order, Medicine


class Model(object):
    def __init__(self, medicines_cnt=10, min_couriers_cnt=1,
                 total_days=45, orders_min_cnt=4, orders_cnt_max_diff=15,
                 extra_cost=0.25, discount=0.05, last_month_discount=0.5):
        self.medicines_cnt = medicines_cnt
        self.min_couriers_cnt = min_couriers_cnt
        self.total_days = total_days
        self.curr_day = 1
        self.extra_cost = extra_cost
        self.discount = discount
        self.big_sum = 1000.0
        self.discount_for_regular = 0.05
        self.max_discount = 0.09
        self.discount_for_big_sum = 0.03
        self.min_orders_pc = 2
        self.max_orders_pc = 4
        self.last_month_discount = last_month_discount
        self.delivery_service = None
        self.medicine_ware_house = None
        self.orders_min_cnt = orders_min_cnt // self.extra_cost
        self.orders_max_cnt = self.orders_min_cnt + randint(7, orders_cnt_max_diff)
        
        self.medicine_names = ["Белосалик", "Акридерм", "Бепантен", "Декспантенол", "Бетасерк",
                               "Быструмгель", "Кетопрофен", "Диклофенак", "Вольтарен", "Гастрозол",
                               "Омепразол", "Детралекс", "Риностоп", "Зантак", "Ранитидин", "Зиртек",
                               "Цетиринакс", "Зовиракс", "Ацикловир", "Иммунал", "Эхинацея", "Имодиум",
                               "Лоперамид", "Йодомарин", "Кавинтон", "Винпоцетин", "Кларитин", "Лорагексал",
                               "Кларитромицин", "Лазолван", "Амброксол", "Ламизил", "Тербинафин", "Ломилан",
                               "Лорагексал", "Максидекс", "Дексаметазон", "Мезим", "Панкреатин", "Но-шпа"]
        
        self.medicine_forms = ["Таблетки", "Суспензия", "Спрей", "Сироп", "Мазь", "Капли"]
        self.medicine_min_dosage = 25
        self.medicine_max_dosage = 250
        self.medicine_min_ttl = 50
        self.medicine_max_ttl = 250
        self.medicine_min_price = 30
        self.medicine_max_price = 3000
        
        self.discount_id_probability = 0.3
        
        self.medicine_min_period = 3
        self.medicine_max_period = 7
        self.periodic_customers = []
        self.periodic_max_quantity = 20
        self.order_max_medicines_quantity = 5
        self.order_max_medicines = 4
        self.request_inst_cnt = 30
        self.medicine_ware_house_min_inst = 5
        
        self.customer_names = ["Маша", "Петя", "Паша", "Катя", "Марина",
                               "Коля", "Вася", "Даша", "Лена", "Боря", "Аркадий",
                               "Настя", "Маруся", "Геракл", "Лев", "Марья", "Игорь",
                               "Матрена", "Никита", "Николай", "Матвей", "Алена", "Кира",
                               "Алиса", "Дмитрий", "Олег", "Диана", "Света", "Жора"]
        self.n_regular_customers = 7
        streets = ['Воробьевы Горы', 'Мичуринский Проспект', 'Лебедева', 'Менделеева', 'Ломоносовский Проспект']
        self.customer_addresses = [streets[randint(0, len(streets) - 1)] + f', {randint(0, 100)}' for _ in
                                   range(100)]
        self.orders_list = []
        self.request = {}
        self.request_time_min = 1
        self.request_time_max = 3
        self.db = {}
        
    
    def generate_medicine_warehouse(self):
        medicines_set = set()
        while len(medicines_set) < self.medicines_cnt:
            medicines_set.add(self.generate_medicine())
        self.medicine_ware_house = MedicineWareHouse(medicines_set,
                                                     min_instances=self.medicine_ware_house_min_inst)
        for medicine in medicines_set:
            self.medicine_ware_house.add_medicine(medicine, quantity=self.request_inst_cnt)
        self.medicine_ware_house.update_quantities()
    
    def generate_medicines_costs(self):
        medicines_set = self.medicine_ware_house.get_medicines_set()
        for medicine in medicines_set:
            self.db['medicines_costs'][medicine.id()] = randint(self.medicine_min_price, self.medicine_max_price)
    
    def generate_delivery_service(self):
        self.delivery_service = DeliveryService(min_couriers=self.min_couriers_cnt, min_orders_pc=self.min_orders_pc,
                                                max_orders_pc=self.max_orders_pc)
    
    def handle_orders(self):
        daily_income = 0.0
        orders, orders_cnt = defaultdict(set), defaultdict(int)
        resolved_orders, resolved_orders_cnt = defaultdict(set), defaultdict(int)
        for order in self.orders_list:
            scale = self.last_month_discount if order.is_sale else 1.0
            income = 0.0
            discount = 0.0
            for medicine, quantity in order.order:
                orders_cnt[medicine.id()] += quantity
                orders[order.id() + f'+is_saile_{order.is_sale}'].add((medicine, quantity))
                medicines, quantity = self.medicine_ware_house.get_medicine(medicine.id(), quantity,
                                                                            is_sale=order.is_sale)
                if quantity > 0:
                    cost = quantity * self.db['medicines_costs'][medicines[0].id()] * scale
                    income += cost
                    resolved_orders[order.id() + f'+is_saile_{order.is_sale}'].add((medicines[0].id(), quantity))
                    resolved_orders_cnt[medicines[0].id()] += quantity
            income *= (1 + self.extra_cost)
            if order.discount_id is not None:
                discount = self.discount
            elif income > self.big_sum:
                discount = self.discount_for_big_sum
            if order.regular:
                discount = min(self.max_discount, discount + self.discount_for_regular)
            income = income * (1 - discount)
            daily_income += income
        orders_cnt['total'] = sum(orders_cnt.values())
        resolved_orders_cnt['total'] = sum(resolved_orders_cnt.values())
        self.db['incomes'][self.curr_day] = daily_income
        self.db[self.curr_day]['orders'] = orders
        self.db[self.curr_day]['resolved_orders'] = resolved_orders
        self.db[self.curr_day]['orders_cnt'] = orders_cnt
        self.db[self.curr_day]['resolved_orders_cnt'] = resolved_orders_cnt
        # if daily_income == 0.0:
        #     raise ValueError()
    
    def add_regular_orders(self):
        for customer in self.db['regular_medicines']:
            order = []
            for medicine, quantity, period in self.db['regular_medicines'][customer]:
                
                if self.curr_day % period == 0:
                    order.append((medicine, quantity))
            if len(order) > 0:
                name, address, phone = customer.split('_')
                discount_id = self.db['discount_ids'][customer]
                self.orders_list.append(Order(phone, address, order, discount_id, is_sale=False, regular=True))
    
    def run(self):
        self.init()
        for day in range(self.total_days):
            self.run_day()
    
    def fulfill_request(self):
        for medicine in self.request:
            if self.request[medicine] == 0:
                self.request[medicine] = -1
                medicine = self.medicine_by_id(medicine)
                self.medicine_ware_house.add_medicine(medicine, self.request_inst_cnt)
                self.db['expenses'][self.curr_day] = self.db['medicines_costs'][medicine.id()] * self.request_inst_cnt
    
    def request_medicines(self):
        required_medicines = self.medicine_ware_house.medicines_to_request
        for medicine, is_required in required_medicines.items():
            if is_required:
                if medicine not in self.request or self.request[medicine] == -1:
                    self.request[medicine] = randint(self.request_time_min, self.request_time_max)
    
    def goto_next_day(self):
        self.curr_day += 1
        self.medicine_ware_house.goto_next_day()
        self.delivery_service.goto_next_day()
        for medicine in self.request:
            if self.request[medicine] > 0:
                self.request[medicine] -= 1
    
    def is_sale(self):
        idx = 0 if randint(1, 100) > 35 else 1
        return [True, False][idx]
    
    def run_day(self):
        self.fulfill_request()
        self.receive_orders()
        self.add_regular_orders()
        self.handle_orders()
        self.deliver_orders()
        print(
            f'day: {self.curr_day}\nincome: {self.db["incomes"][self.curr_day]}, expenses: {self.db["expenses"][self.curr_day] if self.curr_day in self.db["expenses"] else 0}')
        self.goto_next_day()
        self.medicine_ware_house.update_quantities()
        self.request_medicines()
    
    def receive_orders(self):
        self.db[self.curr_day] = {}
        self.db[self.curr_day]['quantities'] = dict(self.medicine_ware_house.get_quantities())
        self.db[self.curr_day]['requests'] = self.get_requests_status()
        orders_cnt = randint(self.orders_min_cnt, self.orders_max_cnt)
        self.orders_list = []
        for _ in range(orders_cnt):
            order = self.generate_order(is_sale=self.is_sale())
            self.orders_list.append(order)
    
    def deliver_orders(self):
        self.delivery_service.distribute(self.orders_list)
        self.db['couriers_overloading'][self.curr_day] = self.delivery_service.get_overloading()
    
    def generate_customer(self):
        name = self.customer_names[randint(0, len(self.customer_names) - 1)]
        address = self.customer_addresses[randint(0, len(self.customer_addresses) - 1)]
        phone_number = self.generate_phone()
        customer = '_'.join([name, address, phone_number])
        if customer in self.db['regular_medicines']:
            discount_id = self.db['discount_ids'][customer]
        else:
            discount_id = self.generate_discount_id(random=True)
        
        return '_'.join([name, address, phone_number]), discount_id
    
    def generate_medicine(self, medicines_set=None):
        if medicines_set is None:
            name = self.medicine_names[randint(0, len(self.medicine_names) - 1)]
            form = self.medicine_forms[randint(0, len(self.medicine_forms) - 1)]
            dosage = str(randint(self.medicine_min_dosage, self.medicine_max_dosage))
            medicine = '_'.join([name, form, dosage])
            if medicine not in self.db['ttls']:
                ttl = randint(self.medicine_min_ttl, self.medicine_max_ttl)
                self.db['ttls'][medicine] = ttl
            else:
                ttl = self.db['ttls'][medicine]
            produced_time = self.curr_day
            return Medicine(name, form, dosage, ttl, produced_time)
        else:
            return [x.change(produced_time=self.curr_day) for x in medicines_set][randint(0, len(medicines_set) - 1)]
    
    def get_requests_status(self):
        requests = []
        for key, value in self.request.items():
            if value != -1:
                requests.append(':'.join([str(key), str(value)]))
        return requests
    
    def generate_phone(self):
        return '+7' + ''.join([str(x) for x in sample(range(0, 10), 10)])
    
    def generate_discount_id(self, random=True):
        if random:
            idx = 1 if (randint(1, 100) / 100) < self.discount_id_probability else 0
            return [None, self.generate_discount_id(random=False)][idx]
        
        return ''.join([str(x) for x in sample(range(0, 10), 5)])
    
    
    def init(self):
        self.init_db()
        self.generate_medicine_warehouse()
        self.generate_medicines_costs()
        self.generate_regular_customers()
        self.generate_delivery_service()
        
    def init_db(self):
        self.db['regular_medicines'] = {}
        self.db['discount_ids'] = {}
        self.db['medicines_costs'] = {}
        self.db['ttls'] = {}
        self.db['incomes'] = {}
        self.db['expenses'] = {}
        self.db['couriers_overloading'] = {}
    
    def generate_regular_customers(self):
        names = sample(self.customer_names, self.n_regular_customers)
        addresses = sample(self.customer_addresses, self.n_regular_customers)
        phones, discount_ids = set(), set()
        while len(phones) < len(names):
            phones.add(self.generate_phone())
        while len(discount_ids) < len(names):
            discount_ids.add(self.generate_discount_id())
        phones, discount_ids = list(phones), list(discount_ids)
        medicines_set = self.medicine_ware_house.get_medicines_set()
        for name, address, phone, discount_id in zip(names, addresses, phones, discount_ids):
            regular_medicines = [
                (medicines_set[randint(0, len(medicines_set) - 1)], randint(1, self.order_max_medicines),
                 randint(self.medicine_min_period, self.medicine_max_period)) for _ in
                range(randint(1, self.order_max_medicines_quantity))
            ]
            customer = '_'.join([name, address, phone])
            self.db['regular_medicines'][customer] = regular_medicines
            self.db['discount_ids'][customer] = discount_id
    
    def medicine_by_id_rand(self, medicine: str):
        name, form, dosage = medicine.split('_')
        form = form if sample([True, False], 1)[0] else None
        dosage = dosage if sample([True, False], 1)[0] else None
        return Medicine(name, form, dosage)
    
    def medicine_by_id(self, id):
        name, form, dosage = id.split('_')
        form = None if form == 'None' else form
        dosage = None if dosage == 'None' else dosage
        ttl = self.db['ttls'][id]
        return Medicine(name, form, dosage, ttl, self.curr_day)
    
    def generate_order(self, is_sale=True, from_available=True):
        customer, discount_id = self.generate_customer()
        name, address, phone = customer.split('_')
        if from_available:
            stock_medicines_set, sale_medicines_set = self.medicine_ware_house.get_available_medicines()
            medicines_set = stock_medicines_set if not is_sale else sale_medicines_set
            if len(medicines_set) == 0:
                medicines_set = [x.id() for x in self.medicine_ware_house.get_medicines_set()]
        else:
            medicines_set = [x.id() for x in self.medicine_ware_house.get_medicines_set()]
        medicines_set = [self.medicine_by_id_rand(x) for x in medicines_set]
        shuffle(medicines_set)
        ordered_medicines = medicines_set[:randint(0, min(self.order_max_medicines, len(medicines_set) - 1)) + 1]
        quantities = [randint(1, self.order_max_medicines_quantity) for _ in range(len(ordered_medicines))]
        order = [(x, c) for x, c in zip(ordered_medicines, quantities)]
        
        return Order(phone, address, order, discount_id, is_sale)


if __name__ == '__main__':
    model = Model()
    model.run()
    
    print('good bye!')
