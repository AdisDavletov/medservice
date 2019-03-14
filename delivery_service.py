class DeliveryService(object):
    def __init__(self, min_couriers=3, max_couriers=9, min_orders_pc=7, max_orders_pc=15):
        self.min_couriers = min_couriers
        self.max_couriers = max_couriers
        self.min_orders_pc = min_orders_pc
        self.max_orders_pc = max_orders_pc
        self.couriers_list = []
        self.n_hired_couriers = 0
        for _ in range(self.min_couriers):
            self.hire()
    
    def goto_next_day(self):
        self.couriers_list = [x.reset() for x in self.couriers_list]
    
    def hire(self):
        self.couriers_list.append(Courier(self.max_orders_pc))
        self.n_hired_couriers += 1
    
    def get_courier_idx(self):
        couriers_list = sorted([(x, i) for i, x in enumerate(self.couriers_list)], key=lambda x: x[0].n_orders_done)
        return couriers_list[0][1]
    
    def distribute(self, delivery_list):
        for _ in delivery_list:
            idx = self.get_courier_idx()
            if self.couriers_list[idx].is_busy():
                if self.n_hired_couriers < self.max_couriers:
                    self.hire()
                    self.couriers_list[-1].n_orders_done += 1
                else:
                    print('too many orders for couriers')
            else:
                self.couriers_list[idx].n_orders_done += 1


class Courier(object):
    def __init__(self, max_orders=15):
        self.n_orders_done = 0
        self.max_orders = max_orders
    
    def is_busy(self):
        return self.n_orders_done == self.max_orders
    
    def reset(self):
        self.n_orders_done = 0
        return self
