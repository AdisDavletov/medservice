from random import randint, shuffle

from customer import Customer
from delivery_service import DeliveryService
from medicin import Medicine
from medicine_ware_house import MedicineWareHouse

MEDICINE_NAMES = ["Белосалик", "Акридерм", "Бепантен", "Декспантенол", "Бетасерк",
                  "Быструмгель", "Кетопрофен", "Диклофенак", "Вольтарен", "Гастрозол",
                  "Омепразол", "Детралекс", "Риностоп", "Зантак", "Ранитидин", "Зиртек",
                  "Цетиринакс", "Зовиракс", "Ацикловир", "Иммунал", "Эхинацея", "Имодиум",
                  "Лоперамид", "Йодомарин", "Кавинтон", "Винпоцетин", "Кларитин", "Лорагексал",
                  "Кларитромицин", "Лазолван", "Амброксол", "Ламизил", "Тербинафин", "Ломилан",
                  "Лорагексал", "Максидекс", "Дексаметазон", "Мезим", "Панкреатин", "Но-шпа"]

MEDICINE_FORMS = ["Таблетки", "Суспензия", "Спрей", "Сироп", "Мазь", "Капли"]


class Model(object):
    def __init__(self, medicines_cnt=10, couriers_cnt=9,
                 days_cnt=45, check_per_day_cnt=9,
                 extra_cost=0.25, discount=0.05):
        self.medicines_cnt = medicines_cnt
        self.couriers_cnt = couriers_cnt
        self.days_cnt = days_cnt
        self.check_per_day_cnt = check_per_day_cnt
        self.curr_day = 0
        self.extra_cost = extra_cost
        self.discount = discount
        self.delivery_service = None
        self.medicine_ware_house = None
        
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
        
        self.medicine_min_period = 1
        self.medicine_max_period = 10
        self.periodic_customers = []
        self.periodic_max_quantity = 20
        self.order_max_medicines_quantity = 10
        self.order_max_medicines = 7
        self.request_inst_cnt = 30
        self.medicine_ware_house_min_inst = 5
        
        self.customer_names = ["Маша", "Петя", "Паша", "Катя", "Марина",
                               "Коля", "Вася", "Даша", "Лена", "Боря", "Аркадий",
                               "Настя", "Маруся", "Геракл", "Лев", "Марья", "Игорь",
                               "Матрена", "Никита", "Николай", "Матвей", "Алена", "Кира",
                               "Алиса", "Дмитрий", "Олег", "Диана", "Света", "Жора"]
        self.n_periodic_customers = 7
        streets = ['Воробьевы Горы', 'Мичуринский Проспект', 'Лебедева', 'Менделеева', 'Ломоносовский Проспект']
        self.customer_addresses = [streets[randint(0, len(streets))] + f', {randint(0, 100)}' for _ in
                                   range(100)]
        self.order_list = []
        self.request_list = []
        self.request_time_min = 1
        self.request_time_max = 3
    
    def create_medicine_ware_house(self):
        self.create_periodic_customers()
        medicines = list(set([self.create_medicine(random=True) for _ in range(self.medicines_cnt * 5)]))[
                    :self.medicines_cnt]
        self.medicine_ware_house = MedicineWareHouse(medicines, medicines * self.request_inst_cnt,
                                                     min_instances=self.medicine_ware_house_min_inst)
    
    def run(self):
        self.create_medicine_ware_house()
        self.delivery_service = DeliveryService()
        for day in range(days_cnt):
            self.run_day()
            self.handle_orders()
            self.deliver_orders()
            self.order_list = []
            self.next_day()
            self.request_medicines()
    
    def fulfill_requests(self):
        for i, (request, t) in enumerate(self.request_list):
            if t == 0:
                self.medicine_ware_house.add_medicines([request] * self.request_inst_cnt)
    
    def request_medicines(self):
        quantity = self.medicine_ware_house.quantity
        min_inst = self.medicine_ware_house.min_instances
        for medicine in quantity.keys():
            if quantity[medicine] - min_inst < 0:
                self.request_list.append((self.medicine_ware_house.get_medicine_by_id_1(medicine),
                                          randint(self.request_time_min, self.request_time_max)))
    
    def next_day(self):
        self.curr_day += 1
        self.medicine_ware_house.next_day()
        self.request_list = [(x, i - 1) for x, i in self.request_list]
    
    def run_day(self):
        for _ in range(self.check_per_day_cnt):
    
    def deliver_orders(self):
        self.delivery_service.distribute(self.order_list)
        self.delivery_service.couriers_list = [x.reset() for x in self.delivery_service.couriers_list]
    
    def create_medicine(self, name='Бромгексин', form=None, dosage=None,
                        ttl=120, price=250, random=False):
        produced_time = self.curr_day
        if random:
            name = self.medicine_names[randint(0, len(self.medicine_names))]
            form = self.medicine_forms[randint(0, len(self.medicine_forms))]
            dosage = randint(self.medicine_min_dosage, self.medicine_max_dosage)
            ttl = randint(self.medicine_min_ttl, self.medicine_max_ttl)
            price = randint(self.medicine_min_price, self.medicine_max_price)
        return Medicine(name, form, dosage, ttl, produced_time, price)
    
    def create_rand_customer(self):
        name = self.customer_names[randint(0, len(self.customer_names))]
        address = self.customer_addresses[randint(0, len(self.customer_addresses))]
        phone_number = ''.join(['+7999'] + [randint(0, 9) for _ in range(7)])
        discount_id = None
        periodic_medicines = None
        period = None
        
        return Customer(name, address, phone_number, discount_id, periodic_medicines, period)
    
    def create_periodic_customers(self):
        names = shuffle(self.customer_names)[:self.n_periodic_customers]
        addresses = shuffle(self.customer_addresses)[:self.n_periodic_customers]
        phones = list(set([''.join(['+7923'] + [randint(0, 9) for _ in range(7)]) for _ in range(100)]))[
                 :self.n_periodic_customers]
        for name, address, phone in zip(names, addresses, phones):
            discount_id = eval(''.join([1] + [randint(0, 9) for _ in range(6)]))
            periodic_medicines = [(self.medicine_ware_house.medicines[
                                       randint(0, len(self.medicine_ware_house.medicines))],
                                   randint(1, self.periodic_max_quantity)) for _ in
                                  range(randint(1, self.order_max_medicines_quantity))]
            period = randint(self.medicine_min_period, self.medicine_max_period)
            
            self.periodic_customers.append(
                Customer(name, address, phone, discount_id, periodic_medicines, period))
    
    def create_order_list(self):
        return [(self.create_medicine(random=True), randint(1, self.order_max_medicines_quantity)) for _ in
                range(randint(1, self.order_max_medicines))]
