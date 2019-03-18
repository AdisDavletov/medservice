import tkinter as tk
from collections import defaultdict
from random import randint, sample, shuffle

from matplotlib import pyplot as plt

from delivery_service import DeliveryService
from medicine_ware_house import MedicineWareHouse, Order, Medicine


class Model(object):
    def __init__(self, medicines_cnt=10, min_couriers_cnt=1, max_couriers_cnt=10,
                 total_days=45, orders_min_cnt=4, orders_cnt_max_diff=15,
                 extra_cost=0.25, discount=0.05, last_month_discount=0.5):
        self.medicines_cnt = medicines_cnt
        self.min_couriers_cnt = min_couriers_cnt
        self.max_couriers_cnt = max_couriers_cnt
        self.total_days = total_days
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
        self.request = None
        self.orders_list = None
        self.request_time_min = 1
        self.request_time_max = 3
        self.db = None
    
    def run(self):
        for day in range(self.total_days):
            self.run_day()
    
    def init(self):
        self.request = {}
        self.orders_list = []
        self.curr_day = 1
        self.init_db()
        self.generate_medicine_warehouse()
        self.generate_medicines_costs()
        self.generate_regular_customers()
        self.generate_delivery_service()
    
    def init_db(self):
        self.db = {}
        self.db['regular_medicines'] = {}
        self.db['discount_ids'] = {}
        self.db['medicines_costs'] = {}
        self.db['ttls'] = {}
        self.db['incomes'] = {}
        self.db['expenses'] = {}
        self.db['couriers_overloading'] = {}
    
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
    
    def generate_delivery_service(self):
        self.delivery_service = DeliveryService(min_couriers=self.min_couriers_cnt, max_couriers=self.max_couriers_cnt,
                                                min_orders_pc=self.min_orders_pc,
                                                max_orders_pc=self.max_orders_pc)
    
    def run_day(self):
        self.fulfill_request()
        self.receive_orders()
        self.add_regular_orders()
        self.handle_orders()
        self.deliver_orders()
        self.goto_next_day()
        self.medicine_ware_house.update_quantities()
        self.request_medicines()
    
    def fulfill_request(self):
        for medicine in self.request:
            if self.request[medicine] == 0:
                self.request[medicine] = -1
                medicine = self.medicine_by_id(medicine)
                self.medicine_ware_house.add_medicine(medicine, self.request_inst_cnt)
                self.db['expenses'][self.curr_day] = self.db['medicines_costs'][medicine.id()] * self.request_inst_cnt
    
    def receive_orders(self):
        self.db[self.curr_day] = {}
        self.db[self.curr_day]['quantities'] = dict(self.medicine_ware_house.get_quantities())
        self.db[self.curr_day]['requests'] = self.get_requests_status()
        orders_cnt = randint(self.orders_min_cnt, self.orders_max_cnt)
        self.orders_list = []
        for _ in range(orders_cnt):
            order = self.generate_order(is_sale=self.is_sale())
            self.orders_list.append(order)
    
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
    
    def deliver_orders(self):
        self.delivery_service.distribute(self.orders_list)
        self.db['couriers_overloading'][self.curr_day] = self.delivery_service.get_overloading()
    
    def goto_next_day(self):
        self.curr_day += 1
        self.medicine_ware_house.goto_next_day()
        self.delivery_service.goto_next_day()
        for medicine in self.request:
            if self.request[medicine] > 0:
                self.request[medicine] -= 1
    
    def request_medicines(self):
        required_medicines = self.medicine_ware_house.medicines_to_request
        for medicine, is_required in required_medicines.items():
            if is_required:
                if medicine not in self.request or self.request[medicine] == -1:
                    self.request[medicine] = randint(self.request_time_min, self.request_time_max)
    
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
    
    def is_sale(self):
        idx = 0 if randint(1, 100) > 35 else 1
        return [True, False][idx]
    
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


class Application(tk.Frame):
    def __init__(self, root, model):
        super().__init__(root)
        self.root = root
        self.model = model
        
        self.build_gui()
    
    def params_widgets(self):
        self.params_frame = tk.Frame(self.upper_root, bg='white', borderwidth=1, relief=tk.SUNKEN)
        self.params_frame.pack(side=tk.RIGHT)
        self.params_total_days = tk.Scale(self.params_frame, orient=tk.HORIZONTAL, length=200,
                                          from_=20, to=180, tickinterval=30, resolution=10, bd=2)
        self.params_extra_cost = tk.Scale(self.params_frame, orient=tk.HORIZONTAL, length=200,
                                          from_=0.01, to=1.0, tickinterval=0.2, resolution=0.01, bd=2)
        self.params_discount = tk.Scale(self.params_frame, orient=tk.HORIZONTAL, length=200,
                                        from_=0.01, to=0.07, tickinterval=0.03, resolution=0.01, bd=2)
        self.params_medicines_cnt = tk.Scale(self.params_frame, orient=tk.HORIZONTAL, length=200,
                                             from_=10, to=100, tickinterval=15, resolution=1, bd=2)
        self.params_couriers_cnt = tk.Scale(self.params_frame, orient=tk.HORIZONTAL, length=200,
                                            from_=5, to=20, tickinterval=5, resolution=1, bd=2)
        self.params_total_days_l = tk.Label(self.params_frame, text='колич. дней:', font='Arial 18', bg='white',
                                            fg='black')
        self.params_extra_cost_l = tk.Label(self.params_frame, text=u'наценка:', font='Arial 18', bg='white',
                                            fg='black')
        self.params_discount_l = tk.Label(self.params_frame, text=u'скидка:', font='Arial 18', bg='white',
                                          fg='black')
        self.params_medicines_cnt_l = tk.Label(self.params_frame, text=u'колич. лекарств:', font='Arial 18',
                                               bg='white', fg='black')
        self.params_couriers_cnt_l = tk.Label(self.params_frame, text=u'макс. колич. курьеров:', font='Arial 18',
                                              bg='white', fg='black')
        
        self.params_total_days.grid(row=0, column=1, padx=7)
        self.params_total_days_l.grid(row=0, column=0, padx=7)
        self.params_extra_cost.grid(row=1, column=1, padx=7)
        self.params_extra_cost_l.grid(row=1, column=0, padx=7)
        self.params_discount.grid(row=2, column=1, padx=7)
        self.params_discount_l.grid(row=2, column=0, padx=7)
        self.params_medicines_cnt.grid(row=3, column=1, padx=7)
        self.params_medicines_cnt_l.grid(row=3, column=0, padx=7)
        self.params_couriers_cnt.grid(row=4, column=1, padx=7)
        self.params_couriers_cnt_l.grid(row=4, column=0, padx=7)
    
    def com_widgets(self):
        self.com_frame = tk.Frame(self.upper_root, bg='white', height=240, borderwidth=1, relief=tk.FLAT)
        self.com_frame.pack(side=tk.LEFT)
        self.button_launch = tk.Button(self.com_frame, text='Запустить', fg='blue', command=self.run)
        # self.button_launch.grid(row=0, column=1, pady=10)
        self.button_next_day = tk.Button(self.com_frame, text='Следующий день', fg='blue', command=self.run_day)
        # self.button_next_day.grid(row=1, column=1, pady=10)
        self.button_show_logs = tk.Button(self.com_frame, text='Показать логи', fg='blue', command=self.show_logs)
        # self.button_show_logs.grid(row=2, column=1, pady=10)
        self.button_show_incomes = tk.Button(self.com_frame, text='Показать прибыль', fg='blue',
                                             command=self.show_incomes)
        # self.button_show_incomes.grid(row=3, column=1, pady=10)
        self.button_show_expenses = tk.Button(self.com_frame, text='Показать убыль', fg='blue',
                                              command=self.show_expenses)
        # self.button_show_expenses.grid(row=4, column=1, pady=10)
        self.button_show_available = tk.Button(self.com_frame, text='Показать доступные лекарства', fg='blue',
                                               command=self.show_available_meds)
        self.button_clear = tk.Button(self.com_frame, text='Очистить', fg='blue', command=self.clear_output)
        self.button_exit = tk.Button(self.com_frame, text='Выйти', fg='blue', command=self.exit)
        
        self.button_launch.pack(padx=17, pady=7)
        self.button_next_day.pack(padx=17, pady=7)
        self.button_show_logs.pack(padx=17, pady=7)
        self.button_show_incomes.pack(padx=17, pady=7)
        self.button_show_expenses.pack(padx=17, pady=7)
        self.button_show_available.pack(padx=17, pady=7)
        self.button_clear.pack(padx=17, pady=7)
        self.button_exit.pack(padx=17, pady=7)
    
    def build_gui(self):
        self.model.init()
        self.upper_root = tk.Frame(self.root)
        self.upper_root.grid(row=0)
        self.lower_root = tk.Frame(self.root)
        self.lower_root.grid(row=1)
        self.params_widgets()
        self.com_widgets()
        self.text = tk.Text(self.lower_root, bd=1, relief=tk.RAISED, font=('times', 12), wrap=tk.WORD)
        self.text.grid(row=0, column=0)
        scr = tk.Scrollbar(self.lower_root, command=self.text.yview)
        self.text.configure(yscrollcommand=scr.set)
        scr.grid(row=0, column=1)
    
    def clear_output(self):
        self.text.delete('1.0', tk.END)
    
    def update_model(self):
        medicines_cnt = int(self.params_medicines_cnt.get())
        extra_cost = float(self.params_extra_cost.get())
        total_days = int(self.params_total_days.get())
        discount = float(self.params_discount.get())
        max_couriers_cnt = int(self.params_couriers_cnt.get())
        self.model.medicines_cnt = medicines_cnt
        self.model.extra_cost = extra_cost
        self.model.total_days = total_days
        self.model.discount = discount
        self.model.max_couriers_cnt = max_couriers_cnt
    
    def run(self):
        self.clear_output()
        self.update_model()
        self.model.init()
        self.text.insert(1.0, f'Происходит моделирование на длительность {self.model.total_days} дней ...\n')
        self.model.run()
        self.text.insert(tk.END, 'Моделирование завершилось!\n')
    
    def run_day(self):
        self.update_model()
        self.text.insert(tk.END, f'Моделирование за {self.model.curr_day}-й день ...\n')
        self.model.run_day()
        self.text.insert(tk.END, 'Моделирование завершилось!\n')
    
    def show_available_meds(self):
        text = '\n'.join([x for x, c in self.model.medicine_ware_house.get_quantities().items() if c > 0]) + '\n'
        self.clear_output()
        self.text.insert(1.0, text)
    
    def generate_plot(self, data):
        keys = [i + 1 for i in range(max(data.keys()))]
        values = [data[k] if k in data else 0 for k in keys]
        plt.plot(keys, values)
        plt.show()
        # plt.savefig('tmp_plot.png', dpi=240, height=100, width=120)
    
    def show_logs(self):
        self.clear_output()
        for i in range(self.model.curr_day - 1):
            self.text.insert(tk.END, f'\nORDERS [day: {i + 1}]\n{self.model.db[i + 1]["orders"].items()}\n')
            self.text.insert(tk.END, f'\nRESOLVED ORDERS\n{self.model.db[i + 1]["resolved_orders"].items()}\n')
    
    def show_incomes(self):
        self.generate_plot(self.model.db['incomes'])
        # self.img = tk.PhotoImage(file='tmp_plot.png')
        self.clear_output()
        # self.text.image_create(1.0, image=self.img)
    
    def show_expenses(self):
        self.generate_plot(self.model.db['expenses'])
        # self.img = tk.PhotoImage(file='tmp_plot.png')
        self.clear_output()
        # self.text.image_create(1.0, image=self.img)
    
    def exit(self):
        self.clear_output()
        self.root.destroy()


if __name__ == '__main__':
    root, model = tk.Tk(), Model()
    application = Application(root, model)
    
    root.title('Аптека')
    root.geometry('700x750+300+20')
    root.resizable(True, False)
    root.mainloop()
