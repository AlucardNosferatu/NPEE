class SwitchingTech:
    LinkCount = 0
    PropDelayPerLink = 0
    TranSpeedPerNode = 0
    MessageCount = 0

    def __init__(self, l_count, pd_per_link, ts_per_node):
        self.LinkCount = l_count
        self.PropDelayPerLink = pd_per_link
        self.TranSpeedPerNode = ts_per_node

    def get_propagation_delay(self):
        return self.PropDelayPerLink * self.LinkCount


class CircuitSwitching(SwitchingTech):
    ConEstablishDelay = 0

    def __init__(self, l_count, pd_per_link, ts_per_node, ce_delay):
        super().__init__(l_count, pd_per_link, ts_per_node)
        self.ConEstablishDelay = ce_delay

    def get_establish_delay(self):
        return self.ConEstablishDelay

    def get_transmission_delay(self, message_count):
        return message_count / self.TranSpeedPerNode

    def get_total_delay(self, message_count):
        delay = 0
        delay += self.get_establish_delay()
        delay += self.get_transmission_delay(message_count)
        delay += self.get_propagation_delay()
        return delay


class MessageSwitching(SwitchingTech):
    StoreDelayPerSwitch = 0

    def __init__(self, l_count, pd_per_link, ts_per_node, sd_per_switch):
        super().__init__(l_count, pd_per_link, ts_per_node)
        self.StoreDelayPerSwitch = sd_per_switch

    def get_transmission_delay(self, message_count):
        return message_count * self.LinkCount / self.TranSpeedPerNode

    def get_store_delay(self):
        return self.StoreDelayPerSwitch * (self.LinkCount - 1)

    def get_total_delay(self, message_count):
        delay = 0
        delay += self.get_transmission_delay(message_count)
        delay += self.get_propagation_delay()
        delay += self.get_store_delay()
        return delay


class PacketSwitching(SwitchingTech):
    StoreDelayPerSwitch = 0
    VirtualCircuit = False
    VCConEstDelay = 0

    def __init__(
            self,
            l_count,
            pd_per_link,
            ts_per_node,
            sd_per_switch,
            vc_ce_delay=None
    ):
        super().__init__(l_count, pd_per_link, ts_per_node)
        self.StoreDelayPerSwitch = sd_per_switch
        self.VirtualCircuit = False
        self.VCConEstDelay = 0
        if type(vc_ce_delay) is int:
            self.VirtualCircuit = True
            self.VCConEstDelay = vc_ce_delay

    def get_establish_delay(self):
        return self.VCConEstDelay

    def get_store_delay(self):
        return self.StoreDelayPerSwitch * (self.LinkCount - 1)

    def get_transmission_delay(self, message_count, packet_length, packet_head):
        packet_count = message_count / packet_length
        if packet_count == int(packet_count):
            packet_count = int(packet_count)
        else:
            packet_count = int(packet_count) + 1
        single_packet_td = (packet_length + packet_head) / self.TranSpeedPerNode
        src_td = packet_count * single_packet_td
        relay_td = (self.LinkCount - 1) * single_packet_td
        return src_td + relay_td

    def get_total_delay(self, message_count, packet_length, packet_head):
        delay = 0
        if self.VirtualCircuit:
            delay += self.get_establish_delay()
        delay += self.get_transmission_delay(message_count, packet_length, packet_head)
        delay += self.get_propagation_delay()
        delay += self.get_store_delay()
        return delay


if __name__ is '__main__':
    ps = PacketSwitching(2, 0.00002, 10000000, 0.000035)
    td = ps.get_total_delay(25 * 1024 * 1024 * 8, 1024*1024, 32)
    print(td)
