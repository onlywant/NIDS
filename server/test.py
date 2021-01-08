# 重组控制器
class IpReassembler:
    # 实现标识和重组数据包的匹配，超时删除功能
    # key的实现 以及<的重写
    # Reassembly buffer identification (key for dict)
    class IpReassemblyBufferKey:
        def __init__(self, fragment=None):
            if fragment == None:
                self.src = 0
                self.dst = 0
                self.proto = ip_field_protocol_t.PROTO_ZERO
                self.id = 0
                self.data = str(self.src) + str(self.dst) + str(self.proto) + str(self.id)
            else:
                self.src = fragment.five_tuple.src_ip
                self.dst = fragment.five_tuple.dst_ip
                self.proto = fragment.five_tuple.ip_proto
                self.id = fragment.id
                self.data = str(self.src) + str(self.dst) + str(self.proto) + str(self.id)

        def __eq__(self, other):
            return hasattr(other, 'data') and self.data == other.data

        def __hash__(self):
            return hash(self.data)

        def __lt__(self, other):
            if self.src < other.src:
                return True
            if self.src > other.src:
                return False
            if self.dst < other.dst:
                return True
            if self.dst > other.dst:
                return False
            if self.id < other.id:
                return True
            if self.id > other.id:
                return False
            return self.proto < other.proto

    def __init__(self):
        self.timeouts = Config()
        self.timeout_interval = IntervalKeeper(self.timeouts.ipfrag_check_interval_ms)
        self.buffer_dict = {}

    # Forwards fragment of fragmented datagram to correct buffer for reassembly.
    def forward_to_buffer(self, fragment):
        key = self.IpReassemblyBufferKey(fragment=fragment)
        # find the
        it = self.buffer_dict.get(key, None)
        if it is not None:
            buffer = it
        else:
            buffer = IpReassemblyBuffer()
            self.buffer_dict[key] = buffer
        # call ip reassembly algorithm
        datagram = buffer.add_fragment(fragment)
        # if new ip datagram reassembled destroy the buffer for it
        # and senqueue datagram to output queue
        if datagram is not None:
            self.buffer_dict.pop(key)
            del buffer
        del fragment
        return datagram

    def check_timeouts(self, now):
        if not self.timeout_interval.is_timedout(now=now):
            self.timeout_interval.end_ts = now
            return
        self.timeout_interval.end_ts = now

        # maximal timestamp that timedout connection can have
        max_timeout_ts = now.get_total_usec() - (self.timeouts.ipfrag_timeout * 1000000)
        for i in list(self.buffer_dict.keys()):
            is_timedout = False
            ipreassemblybuffer = self.buffer_dict[i]
            is_timedout = (ipreassemblybuffer.last_frag_ts.get_total_usec() <= max_timeout_ts)
            if is_timedout:
                print('ip timeout')
                self.buffer_dict.pop(i)


    def reassemble(self, fragment):
        # remove timed out reassembly buffers
        now = fragment.start_ts
        self.check_timeouts(now)

        # check whether packet is part of fragmented datagram
        is_fragmented = (fragment.ip_flag_mf or fragment.ip_frag_offset != 0)
        # if fragmented forward to correct reassembly buffer
        if (is_fragmented):
            return self.forward_to_buffer(fragment=fragment)

        # not fragmented, nothing to do
        return fragment

    def __del__(self):
        self.buffer_dict.clear()
