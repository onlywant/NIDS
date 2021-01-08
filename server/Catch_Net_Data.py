# 实现数据抓取和特征抽取功能（未转换）
from enum import Enum, unique
from scapy.all import *

class SelfQueue:
    # 创立容器
    def __init__(self):
        self.__list = []

    # 入队
    def put(self, item):
        self.__list.append(item)

    # 队头
    def front(self):
        return self.__list[0]

    # 出队
    def get(self):
        return self.__list.pop(0)

    # 判断是否为空
    def is_empty(self):
        return self.__list == []

    # 队列长度
    def size(self):
        return len(self.__list)

# 以太网标志
@unique
class eth_field_type_t(Enum):
    TYPE_ZERO = 0
    MIN_ETH2 = 0x600
    IPV4 = 0x800

# ip协议号
@unique
class ip_field_protocol_t(Enum):
    PROTO_ZERO = 0
    ICMP = 1
    TCP = 6
    UDP = 17

# ICMP类型号
@unique
class icmp_field_type_t(Enum):
    ECHOREPLY = 0
    DEST_UNREACH = 3
    SOURCE_QUENCH = 4
    REDIRECT = 5
    ECHO = 8
    TIME_EXCEEDED = 11
    PARAMETERPROB = 12
    TIMESTAMP = 13
    TIMESTAMPREPLY = 14
    INFO_REQUEST = 15
    INFO_REPLY = 16
    ADDRESS = 17
    ADDRESSREPLY = 18

# 会话状态
@unique
class conversation_state_t(Enum):
    # General states
    INIT = 0  # nothing happened yet.
    SF = 1  # normal establishment and termination. Note that this
    # is same symbol as for state S1. You can tell ther two
    # apart because for S1 there will not be anay byte counts
    # in the summary while for SF there will be. 没有字节可以说SF
    # TCP specific
    S0 = 2  # connection attempt seen no reply.
    S1 = 3  # connection establishedm not terminated.
    S2 = 4  # connection established and close attempt by originator(发起人) seen(but no reply from responder)
    S3 = 5  # Connection established and close attempt by responder seen (but no reply from originator).
    REJ = 6  # Connection attempt rejected.
    RSTOS0 = 7  # Originator sent a SYN followed by a RST, we never saw a SYN-ACK from the responder.
    RSTO = 8  # Connection established, originator aborted (sent a RST).
    RSTR = 9  # Established, responder aborted.
    SH = 10  # Originator sent a SYN followed by a FIN, we never saw a SYN ACK from the responder (hence the connection was 揾alf?open).
    RSTRH = 11  # Responder sent a SYN ACK followed by a RST, we never saw a SYN from the (purported) originator.
    SHR = 12  # Responder sent a SYN ACK followed by a FIN, we never saw a SYN from the originator.
    OTH = 13  # No SYN seen, just midstream traffic (a 損artial connection?that was not later closed).
    # Internal states (TCP-specific)
    ESTAB = 14  # Established - ACK send by originator in S1 state; externally represented as S1
    S4 = 15,  # SYN ACK seen - State between INIT and (RSTRH or SHR); externally represented as OTH
    S2F = 16  # FIN send by responder in state S2 - waiting for final ACK; externally represented as S2
    S3F = 17  # FIN send by originator in state S3 - waiting for final ACK; externally represented as S3

# 会话服务
@unique
class conversation_services_t(Enum):
    # General
    SRV_OTHER = 0
    SRV_PRIVATE = 1

    # ICMP
    SRV_ECR_I = 2
    SRV_URP_I = 3
    SRV_URH_I = 4
    SRV_RED_I = 5
    SRV_ECO_I = 6
    SRV_TIM_I = 7
    SRV_OTH_I = 8

    # UDP
    SRV_DOMAIN_U = 9
    SRV_TFTP_U = 10
    SRV_NTP_U = 11

    # TCP
    SRV_IRC = 12
    SRV_X11 = 13
    SRV_Z39_50 = 14
    SRV_AOL = 15
    SRV_AUTH = 16
    SRV_BGP = 17
    SRV_COURIER = 18
    SRV_CSNET_NS = 19
    SRV_CTF = 20
    SRV_DAYTIME = 21
    SRV_DISCARD = 22
    SRV_DOMAIN = 23
    SRV_ECHO = 24
    SRV_EFS = 25
    SRV_EXEC = 26
    SRV_FINGER = 27
    SRV_FTP = 28
    SRV_FTP_DATA = 29
    SRV_GOPHER = 30
    SRV_HARVEST = 31
    SRV_HOSTNAMES = 32
    SRV_HTTP = 33
    SRV_HTTP_2784 = 34
    SRV_HTTP_443 = 35
    SRV_HTTP_8001 = 36
    SRV_ICMP = 37
    SRV_IMAP4 = 38
    SRV_ISO_TSAP = 39
    SRV_KLOGIN = 40
    SRV_KSHELL = 41
    SRV_LDAP = 42
    SRV_LINK = 43
    SRV_LOGIN = 44
    SRV_MTP = 45
    SRV_NAME = 46
    SRV_NETBIOS_DGM = 47
    SRV_NETBIOS_NS = 48
    SRV_NETBIOS_SSN = 49
    SRV_NETSTAT = 50
    SRV_NNSP = 51
    SRV_NNTP = 52
    SRV_PM_DUMP = 53
    SRV_POP_2 = 54
    SRV_POP_3 = 55
    SRV_PRINTER = 56
    SRV_REMOTE_JOB = 57
    SRV_RJE = 58
    SRV_SHELL = 59
    SRV_SMTP = 60
    SRV_SQL_NET = 61
    SRV_SSH = 62
    SRV_SUNRPC = 63
    SRV_SUPDUP = 64
    SRV_SYSTAT = 65
    SRV_TELNET = 66
    SRV_TIME = 67
    SRV_UUCP = 68
    SRV_UUCP_PATH = 69
    SRV_VMNET = 70
    SRV_WHOIS = 71

    # This must be the last
    NUMBER_OF_SERVICES = 72

# 构造各种超时时间
class Config:
    #	 * Constructor for default timeout values:
    # - IP Fragmentation timeout 30s (Linux default)
    #		http://www.linuxinsight.com/proc_sys_net_ipv4_ipfrag_time.html
    # - Other values derived from iptables doc
    #		http://www.iptables.info/en/connection-state.html
    def __init__(self):
        # 分片重组
        self.ipfrag_timeout = 30
        self.ipfrag_check_interval_ms = 1000
        # 会话重构
        self.tcp_syn_timeout = 120  # S0,S1
        self.tcp_estab_timeout = 5 * 24 * 3600  # ESTAB
        self.tcp_rst_timeout = 10  # REG, RST0, RSTR, RST0S0
        self.tcp_fin_timeout = 120  # S2, S3
        self.tcp_last_ack_timeout = 30  # S2F, S3F
        self.udp_timeout = 180
        self.icmp_timeout = 30
        self.conversation_check_interval_ms = 1000
        # 统计
        self.time_window_ms = 2000
        self.count_window_size = 100

# 时间戳，
class TimeStamp:
    def __init__(self, usec=0):
        self.sec = usec // 1000000
        self.usec = usec % 1000000

    def set_time(self, usec):
        self.sec = usec // 1000000
        self.usec = usec % 1000000

    def get_total_usec(self):
        return self.sec * 1000000 + self.usec

# 时间间隔（默认1s，判断是否超时）
class IntervalKeeper:
    # 1s interval
    def __init__(self, interval_ms=None):
        if interval_ms is not None:
            self.interval = interval_ms * 1000
        else:
            self.interval = 0  # in us
        self.end_ts = TimeStamp()

    def is_timedout(self, now):
        return now.get_total_usec() >= self.end_ts.get_total_usec() + self.interval

# 数据包五元组，hash唯一标识
class FiveTuple:
    def __init__(self):
        self.ip_proto = ip_field_protocol_t.PROTO_ZERO
        self.src_ip = 0
        self.dst_ip = 0
        self.src_port = 0
        self.dst_port = 0
        self.data = None

    def set_data(self):
        self.data = str(self.ip_proto) + str(self.src_ip) + str(self.dst_ip) + str(self.src_port) + str(self.dst_port)

    def land(self):
        # 若连接来自/送达同一个主机/端口则为1，否则为0，离散类型，0或1。
        if (self.src_ip == self.dst_ip and self.src_port == self.dst_port):
            return 1
        return 0

    def reversed(self):
        # 返回一个调换的FiveTuple
        a = FiveTuple()
        a.ip_proto = self.ip_proto
        a.src_ip = self.dst_ip
        a.dst_ip = self.src_ip
        a.src_port = self.dst_port
        a.dst_port = self.src_port
        a.set_data()
        return a

    def __eq__(self, other):
        return hasattr(other, 'data') and self.data == other.data

    def __hash__(self):
        return hash(self.data)

# 数据包基本数据
class Package:
    # source data
    def __init__(self, pac=None):
        if pac is not None:
            self.start_ts = pac.start_ts
            self.five_tuple = pac.five_tuple
            self.eth_type = pac.eth_type
            self.tcp_flags = pac.tcp_flags
            self.icmp_type = pac.icmp_type
            self.icmp_code = pac.icmp_code
            self.length = pac.length
        else:
            self.start_ts = TimeStamp()
            self.five_tuple = FiveTuple()
            self.eth_type = eth_field_type_t.TYPE_ZERO
            self.tcp_flags = None
            self.icmp_type = icmp_field_type_t.ECHOREPLY
            self.icmp_code = 0
            self.length = 0

    def fin(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x01 != 0)

    def syn(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x02 != 0)

    def rst(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x04 != 0)

    def psh(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x08 != 0)

    def ack(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x10 != 0)

    def urg(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x20 != 0)

    def ece(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x40 != 0)

    def cwr(self):
        if self.tcp_flags is None:
            return False
        else:
            return (self.tcp_flags & 0x80 != 0)

# 数据包分片
class IpFragment(Package):
    def __init__(self, pac=None):
        super(IpFragment, self).__init__(pac=pac)
        self.ip_frag_offset = 0
        self.id = 0
        self.ip_flag_mf = False
        self.ip_payload_length = 0

    def show(self):
        print('start_ts =', self.start_ts.get_total_usec(),
              self.five_tuple.src_ip, ' -> ', self.five_tuple.dst_ip,
              self.id, self.ip_payload_length)

# 数据包重组后
class IpDatagram(Package):
    def __init__(self, pac=None):
        super(IpDatagram, self).__init__(pac=pac)
        self.end_ts = TimeStamp()
        self.frame_count = 0

    def show(self):
        print(self.five_tuple.src_ip, '->', self.five_tuple.dst_ip,
              self.length, self.five_tuple.ip_proto, '\n',
              'tcp_flag =', self.tcp_flags,
              'icmp_flag =', self.icmp_type, self.icmp_code)

# 重组缓冲区洞链表
class IpReassemblyBufferHoleList:
    # 重组算法
    class Hole:
        def __init__(self, fi=0, la=sys.maxsize, ne=None):
            self.first = fi
            self.last = la
            self.next = ne

    def __init__(self):
        self.head = self.Hole()

    def is_empty(self):
        return self.head == None

    def add_fragment(self, frag_first, frag_last, is_last_frag):
        # 更新洞的状态，比如这个片段会填补哪个地方
        prev = None
        hole = self.head
        while hole is not None:
            # 没有下一描述符停止
            while hole is not None and (frag_first > hole.last or frag_last < hole.first):
                prev = hole
                hole = hole.next
            if hole is not None:
                ne = hole.next
                if prev is not None:
                    prev.next = ne
                else:
                    self.head = ne
                # 5. 分片前产生的洞
                if frag_first > hole.first:
                    new_hole = self.Hole(fi=hole.first, la=frag_last - 1, ne=ne)
                    if prev is not None:
                        prev.next = new_hole
                    else:
                        self.head = new_hole
                    prev = new_hole
                # 6.分片后产生的洞
                if is_last_frag and ne is None:
                    hole.last = frag_last
                if frag_last < hole.last:
                    new_hole = self.Hole(fi=frag_last + 1, la=hole.last, ne=ne)
                    if prev != None:
                        prev.next = new_hole
                    else:
                        self.head = new_hole
                    prev = new_hole
                del hole
                hole = ne

# 重组缓冲区
class IpReassemblyBuffer:
    # 重组缓冲区
    def __init__(self):
        self.hole_list = IpReassemblyBufferHoleList()
        self.datagram = None
        self.first_frag_ts = TimeStamp()
        self.last_frag_ts = TimeStamp()
        self.frame_count = 0
        self.tot_len = 0

    def add_fragment(self, fragment):
        if self.datagram == None and fragment.ip_frag_offset == 0:
            self.datagram = IpDatagram(pac=fragment)
            self.tot_len = fragment.length - fragment.ip_payload_length
        # 时间戳、计数、长度
        if self.frame_count == 0:
            self.first_frag_ts = fragment.start_ts
        self.last_frag_ts = fragment.start_ts  # fragment 只有start_ts
        self.frame_count += 1
        self.tot_len += fragment.ip_payload_length

        # mf = 0 当且仅当最后一个分片
        is_last_frag = not fragment.ip_flag_mf
        frag_first = fragment.ip_frag_offset * 8
        frag_last = frag_first + fragment.ip_payload_length - 1

        # 填洞
        self.hole_list.add_fragment(frag_first=frag_first, frag_last=frag_last, is_last_frag=is_last_frag)

        # 没有洞存在即完成
        if self.hole_list.is_empty():
            # 更新数据
            self.datagram.start_ts = self.first_frag_ts
            self.datagram.end_ts = self.last_frag_ts
            self.datagram.frame_count = self.frame_count
            self.datagram.length = self.tot_len
            return self.datagram
        return None

# 重组控制器
class IpReassembler:
    # 实现标识和重组数据包的匹配，超时删除功能
    # key的实现 以及<的重写
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

    # 转发碎片数据报的碎片，以纠正用于重新组装的缓冲区。
    def forward_to_buffer(self, fragment):
        key = self.IpReassemblyBufferKey(fragment=fragment)
        # find the
        it = self.buffer_dict.get(key, None)
        if it is not None:
            buffer = it
        else:
            buffer = IpReassemblyBuffer()
            self.buffer_dict[key] = buffer
        # 调用重组算法
        datagram = buffer.add_fragment(fragment)
        # 如果重新组装新的ip数据报，销毁它的缓冲区
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

        # 输出连接可能具有的最大时间戳
        max_timeout_ts = now.get_total_usec() - (self.timeouts.ipfrag_timeout * 1000000)
        for i in list(self.buffer_dict.keys()):
            is_timedout = False
            ipreassemblybuffer = self.buffer_dict[i]
            is_timedout = (ipreassemblybuffer.last_frag_ts.get_total_usec() <= max_timeout_ts)
            if is_timedout:
                print('ip timeout')
                self.buffer_dict.pop(i)


    def reassemble(self, fragment):
        # 移除超时的重新组装缓冲区
        now = fragment.start_ts
        self.check_timeouts(now)

        # 检查数据包是否是片段数据报的一部分
        is_fragmented = (fragment.ip_flag_mf or fragment.ip_frag_offset != 0)
        # 如果前向分段，请更正重新组装缓冲区
        if (is_fragmented):
            return self.forward_to_buffer(fragment=fragment)

        return fragment

    def __del__(self):
        self.buffer_dict.clear()

# 会话
class Conversation:
    # 服务名称
    SERVICE_NAMES = [
        # General
        "other",
        "private",

        # ICMP
        "ecr_i",
        "urp_i",
        "urh_i",
        "red_i",
        "eco_i",
        "tim_i",
        "oth_i",

        # UDP
        "domain_u",
        "tftp_u",
        "ntp_u",

        # TCP
        "IRC",
        "X11",
        "Z39_50",
        "aol",
        "auth",
        "bgp",
        "courier",
        "csnet_ns",
        "ctf",
        "daytime",
        "discard",
        "domain",
        "echo",
        "efs",
        "exec",
        "finger",
        "ftp",
        "ftp_data",
        "gopher",
        "harvest",
        "hostnames",
        "http",
        "http_2784",
        "http_443",
        "http_8001",
        "icmp",
        "imap4",
        "iso_tsap",
        "klogin",
        "kshell",
        "ldap",
        "link",
        "login",
        "mtp",
        "name",
        "netbios_dgm",
        "netbios_ns",
        "netbios_ssn",
        "netstat",
        "nnsp",
        "nntp",
        "pm_dump",
        "pop_2",
        "pop_3",
        "printer",
        "remote_job",
        "rje",
        "shell",
        "smtp",
        "sql_net",
        "ssh",
        "sunrpc",
        "supdup",
        "systat",
        "telnet",
        "time",
        "uucp",
        "uucp_path",
        "vmnet",
        "whois"]
    # 状态名称
    STATE_NAMES = ['INIT', 'SF', 'S0', 'S1', 'S2', 'S3', 'REJ', 'RSTOS0', 'RSTO',
                   'RSTR', 'SH', 'RSTSH', 'SHR', 'OTH', 'ESTAB', 'S4', 'S2F', 'S3F']

    def __init__(self, tuple=None, packet=None):
        if tuple is not None:
            self.five_tuple = tuple
        if packet is not None:
            self.five_tuple = packet.five_tuple
        self.state = conversation_state_t.INIT  # feature 2,3,7(land)
        self.start_ts = TimeStamp()  # 计算 duration
        self.end_ts = TimeStamp()  # 计算 duration   feature 1
        self.packets = 0
        self.src_packets = 0
        self.dst_packets = 0
        self.land = self.five_tuple.land()
        self.src_bytes = 0  # feature 5
        self.dst_bytes = 0  # feature 6
        self.wrong_fragment = 0  # feature 8
        self.urgent_packets = 0  # feature 9
    # 将新的数据包添加至会话
    def add_packet(self, pac):
        # 如果该会话没有数据包
        # print(pac.length)
        if self.packets == 0:
            self.start_ts = pac.start_ts
        self.end_ts = pac.start_ts
        if pac.five_tuple.src_ip == self.five_tuple.src_ip:
            self.src_packets += 1
            self.src_bytes += pac.length

        else:
            self.dst_bytes += pac.length
            self.dst_packets += 1
        self.packets += 1
        if pac.urg():
            self.urgent_packets += 1
        self.update_state(pac)
        # print('proto:',self.five_tuple.ip_proto,'src_bytes:',self.src_bytes,'dst_bytes:', self.dst_bytes, 'state:',self.state_to_string())
        return self.is_final_state()
    # 更新会话状态
    def update_state(self, packet):
        # TODO 完成状态更新
        self.state = conversation_state_t.SF
    # 获取会话状态 Feature 4
    def get_state(self):
        switcher = {
            conversation_state_t.S1: conversation_state_t.S0,
            conversation_state_t.ESTAB: conversation_state_t.S1,
            conversation_state_t.S4: conversation_state_t.OTH,
            conversation_state_t.SHR: conversation_state_t.OTH,
            conversation_state_t.RSTRH: conversation_state_t.OTH,
            conversation_state_t.S2F: conversation_state_t.S2,
            conversation_state_t.S3F: conversation_state_t.S3
        }
        return switcher.get(self.state, self.state)
    # 获取会话名称
    def state_to_string(self):
        return self.STATE_NAMES[self.get_state().value]
    # 是否是结束状态
    def is_final_state(self):
        # TODO TCP subclass override
        return False
    #
    def is_serror(self):
        x = self.get_state()
        if x == conversation_state_t.S0 or x == conversation_state_t.S1 or\
            x == conversation_state_t.S2 or x == conversation_state_t.S3:
            return True
        return False
    #
    def is_rerror(self):
        return self.get_state() == conversation_state_t.REJ
    # 获取string的协议特征 Feature 2
    def get_protocol_type_to_string(self):
        switcher = {
            ip_field_protocol_t.TCP.value: 'tcp',
            ip_field_protocol_t.UDP.value: 'udp',
            ip_field_protocol_t.ICMP.value: 'icmp'
        }
        return switcher.get(self.five_tuple.ip_proto, "UNKNOWN")
    # 获取会话持续时间 Feature 1
    def get_duration(self):
        return self.end_ts.get_total_usec() - self.start_ts.get_total_usec()

    def __lt__(self, other):
        return self.end_ts.get_total_usec() < other.end_ts.get_total_usec()

    def features(self, ret):
        ret.append(self.get_duration() // 1000000)
        ret.append(self.get_protocol_type_to_string())
        ret.append(self.state_to_string())
        ret.append(self.src_bytes)
        ret.append(self.dst_bytes)
        ret.append(self.land)
        ret.append(self.wrong_fragment)
        ret.append(self.urgent_packets)

# TCP会话
class TCPConversation(Conversation):
    # TODO
    def update_state(self, packet):
        # 判断是源还是目标
        originator = (self.five_tuple.src_ip == packet.five_tuple.src_ip)
        if self.state == conversation_state_t.INIT:
            if originator:
                if packet.syn():
                    self.state = conversation_state_t.S0
            else:
                if packet.syn() and packet.ack():
                    self.state = conversation_state_t.S4

        elif self.state == conversation_state_t.S0:
            if originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTOS0
                elif packet.fin():
                    self.state = conversation_state_t.SH
            else:
                if packet.rst():
                    self.state = conversation_state_t.REJ
                elif packet.syn() and packet.ack():
                    self.state = conversation_state_t.S1
        elif self.state == conversation_state_t.S4:
            if not originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTRH
                elif packet.fin():
                    self.state = conversation_state_t.SHR
        elif self.state == conversation_state_t.S1:
            if originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTO
                elif packet.ack():
                    self.state = conversation_state_t.ESTAB
            else:
                if packet.rst():
                    self.state = conversation_state_t.RSTR
        elif self.state == conversation_state_t.ESTAB:
            if originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTO
                elif packet.fin():
                    self.state = conversation_state_t.S2
            else:
                if packet.rst():
                    self.state = conversation_state_t.RSTR
                elif packet.fin():
                    self.state = conversation_state_t.S3
        elif self.state == conversation_state_t.S2:
            if originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTO
            else:
                if packet.rst():
                    self.state = conversation_state_t.RSTR
                elif packet.fin():
                    self.state = conversation_state_t.S2F
        elif self.state == conversation_state_t.S3:
            if originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTO
                elif packet.fin():
                    self.state = conversation_state_t.S3F
            else:
                if packet.rst():
                    self.state = conversation_state_t.RSTR
        elif self.state == conversation_state_t.S2F:
            if originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTO
                elif packet.ack():
                    self.state = conversation_state_t.SF
            else:
                if packet.rst():
                    self.state = conversation_state_t.RSTR
        elif self.state == conversation_state_t.S3F:
            if originator:
                if packet.rst():
                    self.state = conversation_state_t.RSTO
            else:
                if packet.rst():
                    self.state = conversation_state_t.RSTR
                elif packet.ack():
                    self.state = conversation_state_t.SF

    def is_final_state(self):
        if self.state == conversation_state_t.INIT or \
                self.state == conversation_state_t.S0 or \
                self.state == conversation_state_t.S1 or \
                self.state == conversation_state_t.S4 or \
                self.state == conversation_state_t.ESTAB or \
                self.state == conversation_state_t.S2 or \
                self.state == conversation_state_t.S3 or \
                self.state == conversation_state_t.S2F or \
                self.state == conversation_state_t.S3F or \
                self.state == conversation_state_t.REJ or\
                self.state == conversation_state_t.RSTO or\
                self.state == conversation_state_t.RSTR or\
                self.state == conversation_state_t.RSTOS0:
            return False
        else:
            return True
    # 获取服务特征 Feature 3
    def get_service(self):
        if self.five_tuple.src_port == 20:
            return conversation_services_t.SRV_FTP_DATA
        if self.five_tuple.dst_port >= 49152:
            return conversation_services_t.SRV_PRIVATE
        switcher = {
            # Internet Relay Chat via TLS/SSL
            194: conversation_services_t.SRV_IRC,
            529: conversation_services_t.SRV_IRC,
            2218: conversation_services_t.SRV_IRC,
            6665: conversation_services_t.SRV_IRC,
            6666: conversation_services_t.SRV_IRC,
            6668: conversation_services_t.SRV_IRC,
            6669: conversation_services_t.SRV_IRC,
            6697: conversation_services_t.SRV_IRC,
            # X Window System (6000-6063)
            6000: conversation_services_t.SRV_X11,
            6001: conversation_services_t.SRV_X11,
            6002: conversation_services_t.SRV_X11,
            6003: conversation_services_t.SRV_X11,
            6004: conversation_services_t.SRV_X11,
            6005: conversation_services_t.SRV_X11,
            6006: conversation_services_t.SRV_X11,
            6007: conversation_services_t.SRV_X11,
            6008: conversation_services_t.SRV_X11,
            6009: conversation_services_t.SRV_X11,
            6010: conversation_services_t.SRV_X11,
            6011: conversation_services_t.SRV_X11,
            6012: conversation_services_t.SRV_X11,
            6013: conversation_services_t.SRV_X11,
            6014: conversation_services_t.SRV_X11,
            6015: conversation_services_t.SRV_X11,
            6016: conversation_services_t.SRV_X11,
            6017: conversation_services_t.SRV_X11,
            6018: conversation_services_t.SRV_X11,
            6019: conversation_services_t.SRV_X11,
            6020: conversation_services_t.SRV_X11,
            6021: conversation_services_t.SRV_X11,
            6022: conversation_services_t.SRV_X11,
            6023: conversation_services_t.SRV_X11,
            6024: conversation_services_t.SRV_X11,
            6025: conversation_services_t.SRV_X11,
            6026: conversation_services_t.SRV_X11,
            6027: conversation_services_t.SRV_X11,
            6028: conversation_services_t.SRV_X11,
            6029: conversation_services_t.SRV_X11,
            6030: conversation_services_t.SRV_X11,
            6031: conversation_services_t.SRV_X11,
            6032: conversation_services_t.SRV_X11,
            6033: conversation_services_t.SRV_X11,
            6034: conversation_services_t.SRV_X11,
            6035: conversation_services_t.SRV_X11,
            6036: conversation_services_t.SRV_X11,
            6037: conversation_services_t.SRV_X11,
            6038: conversation_services_t.SRV_X11,
            6039: conversation_services_t.SRV_X11,
            6040: conversation_services_t.SRV_X11,
            6041: conversation_services_t.SRV_X11,
            6042: conversation_services_t.SRV_X11,
            6043: conversation_services_t.SRV_X11,
            6044: conversation_services_t.SRV_X11,
            6045: conversation_services_t.SRV_X11,
            6046: conversation_services_t.SRV_X11,
            6047: conversation_services_t.SRV_X11,
            6048: conversation_services_t.SRV_X11,
            6049: conversation_services_t.SRV_X11,
            6050: conversation_services_t.SRV_X11,
            6051: conversation_services_t.SRV_X11,
            6052: conversation_services_t.SRV_X11,
            6053: conversation_services_t.SRV_X11,
            6054: conversation_services_t.SRV_X11,
            6055: conversation_services_t.SRV_X11,
            6056: conversation_services_t.SRV_X11,
            6057: conversation_services_t.SRV_X11,
            6058: conversation_services_t.SRV_X11,
            6059: conversation_services_t.SRV_X11,
            6060: conversation_services_t.SRV_X11,
            6061: conversation_services_t.SRV_X11,
            6062: conversation_services_t.SRV_X11,
            6063: conversation_services_t.SRV_X11,
            # ANSI Z39.50
            210: conversation_services_t.SRV_Z39_50,
            # America-Online  AOL Instant Messenger
            5190: conversation_services_t.SRV_AOL,
            5191: conversation_services_t.SRV_AOL,
            5192: conversation_services_t.SRV_AOL,
            5193: conversation_services_t.SRV_AOL,
            531: conversation_services_t.SRV_AOL,

            113: conversation_services_t.SRV_AUTH,  # Authentication Service
            31: conversation_services_t.SRV_AUTH,  # MSG Authentication
            56: conversation_services_t.SRV_AUTH,  # XNS Authentication
            222: conversation_services_t.SRV_AUTH,  # Berkeley rshd with SPX auth
            353: conversation_services_t.SRV_AUTH,  # NDSAUTH
            370: conversation_services_t.SRV_AUTH,  # codaauth2
            1615: conversation_services_t.SRV_AUTH,  # NetBill Authorization Server
            2139: conversation_services_t.SRV_AUTH,  # IAS-AUTH
            2147: conversation_services_t.SRV_AUTH,  # Live Vault Authentication
            2334: conversation_services_t.SRV_AUTH,  # ACE Client Auth
            2392: conversation_services_t.SRV_AUTH,  # Tactical Auth
            2478: conversation_services_t.SRV_AUTH,  # SecurSight Authentication Server (SSL)
            2821: conversation_services_t.SRV_AUTH,  # VERITAS Authentication Service
            3113: conversation_services_t.SRV_AUTH,  # CS-Authenticate Svr Port
            3207: conversation_services_t.SRV_AUTH,  # Veritas Authentication Port
            3710: conversation_services_t.SRV_AUTH,  # PortGate Authentication
            3799: conversation_services_t.SRV_AUTH,  # RADIUS Dynamic Authorization
            3810: conversation_services_t.SRV_AUTH,  # WLAN AS server
            3833: conversation_services_t.SRV_AUTH,  # AIPN LS Authentication
            3871: conversation_services_t.SRV_AUTH,  # Avocent DS Authorization
            4032: conversation_services_t.SRV_AUTH,  # VERITAS Authorization Service
            4129: conversation_services_t.SRV_AUTH,  # NuFW authentication protocol
            4373: conversation_services_t.SRV_AUTH,  # NuFW authentication protocol
            5067: conversation_services_t.SRV_AUTH,  # Authentx Service
            5635: conversation_services_t.SRV_AUTH,  # SFM Authentication Subsystem
            6268: conversation_services_t.SRV_AUTH,  # Grid Authentication
            6269: conversation_services_t.SRV_AUTH,  # Grid Authentication Alt
            7004: conversation_services_t.SRV_AUTH,  # AFS/Kerberos authentication service
            7847: conversation_services_t.SRV_AUTH,  # A product key authentication protocol made by CSO
            9002: conversation_services_t.SRV_AUTH,  # DynamID authentication
            19194: conversation_services_t.SRV_AUTH,  # UserAuthority SecureAgent
            27999: conversation_services_t.SRV_AUTH,  # TW Authentication/Key Distribution and

            179: conversation_services_t.SRV_BGP,  # Border Gateway Protocol
            530: conversation_services_t.SRV_COURIER,  # rpc
            165: conversation_services_t.SRV_COURIER,  # Xerox (xns-courier)
            105: conversation_services_t.SRV_CSNET_NS,  # Mailbox Name Nameserver
            84: conversation_services_t.SRV_CTF,  # Common Trace Facility
            13: conversation_services_t.SRV_DAYTIME,  # Daytime
            9: conversation_services_t.SRV_DISCARD,
            53: conversation_services_t.SRV_DOMAIN,
            7: conversation_services_t.SRV_ECHO,
            520: conversation_services_t.SRV_EFS,  # extended file name server
            512: conversation_services_t.SRV_EXEC,
            # remote process execution; authentication performed using passwords and UNIX login names
            79: conversation_services_t.SRV_FINGER,
            21: conversation_services_t.SRV_FTP,
            20: conversation_services_t.SRV_FTP_DATA,
            70: conversation_services_t.SRV_GOPHER,
            101: conversation_services_t.SRV_HOSTNAMES,
            80: conversation_services_t.SRV_HTTP,
            8080: conversation_services_t.SRV_HTTP,
            8008: conversation_services_t.SRV_HTTP,
            2784: conversation_services_t.SRV_HTTP_2784,
            443: conversation_services_t.SRV_HTTP_443,
            8001: conversation_services_t.SRV_HTTP_8001,
            5813: conversation_services_t.SRV_ICMP,
            143: conversation_services_t.SRV_IMAP4,
            993: conversation_services_t.SRV_IMAP4,
            102: conversation_services_t.SRV_ISO_TSAP,
            309: conversation_services_t.SRV_ISO_TSAP,
            543: conversation_services_t.SRV_KLOGIN,
            544: conversation_services_t.SRV_KSHELL,
            389: conversation_services_t.SRV_LDAP,
            636: conversation_services_t.SRV_LDAP,
            245: conversation_services_t.SRV_LINK,
            513: conversation_services_t.SRV_LOGIN,
            1911: conversation_services_t.SRV_MTP,
            42: conversation_services_t.SRV_NAME,
            138: conversation_services_t.SRV_NETBIOS_DGM,
            137: conversation_services_t.SRV_NETBIOS_NS,
            139: conversation_services_t.SRV_NETBIOS_SSN,
            15: conversation_services_t.SRV_NETSTAT,
            433: conversation_services_t.SRV_NNSP,
            119: conversation_services_t.SRV_NNTP,
            563: conversation_services_t.SRV_NNTP,
            109: conversation_services_t.SRV_POP_2,
            110: conversation_services_t.SRV_POP_3,
            515: conversation_services_t.SRV_PRINTER,
            71: conversation_services_t.SRV_REMOTE_JOB,
            72: conversation_services_t.SRV_REMOTE_JOB,
            73: conversation_services_t.SRV_REMOTE_JOB,
            74: conversation_services_t.SRV_REMOTE_JOB,
            5: conversation_services_t.SRV_RJE,
            77: conversation_services_t.SRV_RJE,
            514: conversation_services_t.SRV_SHELL,
            25: conversation_services_t.SRV_SMTP,
            66: conversation_services_t.SRV_SQL_NET,
            150: conversation_services_t.SRV_SQL_NET,
            22: conversation_services_t.SRV_SSH,
            111: conversation_services_t.SRV_SUNRPC,
            95: conversation_services_t.SRV_SUPDUP,
            11: conversation_services_t.SRV_SYSTAT,
            23: conversation_services_t.SRV_TELNET,
            37: conversation_services_t.SRV_TIME,
            540: conversation_services_t.SRV_UUCP,
            4031: conversation_services_t.SRV_UUCP,
            117: conversation_services_t.SRV_UUCP_PATH,
            175: conversation_services_t.SRV_VMNET,
            43: conversation_services_t.SRV_WHOIS,
            4321: conversation_services_t.SRV_WHOIS
        }
        return switcher.get(self.five_tuple.dst_port, conversation_services_t.SRV_OTHER)

    def features(self):
        ret = []
        super(TCPConversation, self).features(ret=ret)
        ret.insert(2, self.SERVICE_NAMES[self.get_service().value])
        return ret

# UDP会话
class UDPConversation(Conversation):
    # 获取服务特征 Feature 3
    def get_service(self):
        if self.five_tuple.dst_port >= 49152:
            return conversation_services_t.SRV_PRIVATE
        switcher = {
            53: conversation_services_t.SRV_DOMAIN_U,
            69: conversation_services_t.SRV_TFTP_U,
            123: conversation_services_t.SRV_NTP_U
        }
        return switcher.get(self.five_tuple.dst_port, conversation_services_t.SRV_OTHER)

    def features(self):
        ret = []
        super(UDPConversation, self).features(ret=ret)
        ret.insert(2, self.SERVICE_NAMES[self.get_service().value])
        return ret

# ICMP会话
class ICMPConversation(Conversation):
    def __init__(self, tuple=None, packet=None):
        super(ICMPConversation, self).__init__(tuple=tuple, packet=packet)
        if packet is not None:
            self.icmp_type = packet.icmp_type
            self.icmp_code = packet.icmp_code
        else:
            self.icmp_type = icmp_field_type_t.ECHOREPLY.value
            self.icmp_code = 0

    # 获取服务特征 Feature 3
    def get_service(self):
        if self.icmp_type == icmp_field_type_t.DEST_UNREACH.value:
            if self.icmp_code == 0:
                return conversation_services_t.SRV_URP_I
            elif self.icmp_code == 1:
                return conversation_services_t.SRV_URH_I
            else:
                return conversation_services_t.SRV_OTH_I
        switcher = {
            icmp_field_type_t.ECHOREPLY.value: conversation_services_t.SRV_ECR_I,
            icmp_field_type_t.REDIRECT.value: conversation_services_t.SRV_RED_I,
            icmp_field_type_t.ECHO.value: conversation_services_t.SRV_ECO_I,
            icmp_field_type_t.TIME_EXCEEDED.value: conversation_services_t.SRV_TIM_I
        }
        return switcher.get(self.icmp_type, conversation_services_t.SRV_OTH_I)

    def features(self):
        ret = []
        super(ICMPConversation, self).features(ret=ret)
        ret.insert(2, self.SERVICE_NAMES[self.get_service().value])
        return ret

# 会话重构器
class ConversationReconstructor:
    def __init__(self, config=None):
        if config is not None:
            self.timeouts = config
        else:
            self.timeouts = Config()
        self.output_queue = SelfQueue()
        self.conv_map = {}
        self.timeout_interval = IntervalKeeper(self.timeouts.conversation_check_interval_ms)

    def add_packet(self, pac):
        # 删除超时的重新组装对话
        now = pac.start_ts
        self.check_timeouts(now)
        key = pac.five_tuple
        conv = None
        ip_proto = pac.five_tuple.ip_proto
        # 找 或 插入
        conv = self.conv_map.get(key, None)
        # 如果没有找到，试着用相反的方向
        if conv is None:
            if ip_proto == 6 or ip_proto == 17:
                rev_key = key.reversed()
                conv = self.conv_map.get(rev_key, None)
                if conv is not None:
                    key = rev_key
        if conv is None:
            if ip_proto == 6:
                conv = TCPConversation(packet=pac)
            elif ip_proto == 17:
                conv = UDPConversation(packet=pac)
            elif ip_proto == 1:
                conv = ICMPConversation(packet=pac)
            self.conv_map[key] = conv
        is_finished = conv.add_packet(pac=pac)
        if is_finished:
            self.conv_map.pop(key)
            self.output_queue.put(conv)

    def check_timeouts(self, now):
        if not self.timeout_interval.is_timedout(now=now):
            self.timeout_interval.end_ts = now
            return
        self.timeout_interval.end_ts = now

        # 输出连接可能具有的最大时间戳
        max_tcp_syn = now.get_total_usec() - (self.timeouts.tcp_syn_timeout * 1000000)
        max_tcp_estab = now.get_total_usec() - (self.timeouts.tcp_estab_timeout * 1000000)
        max_tcp_rst = now.get_total_usec() - (self.timeouts.tcp_rst_timeout * 1000000)
        max_tcp_fin = now.get_total_usec() - (self.timeouts.tcp_fin_timeout * 1000000)
        max_tcp_last_ack = now.get_total_usec() - (self.timeouts.tcp_last_ack_timeout * 1000000)
        max_udp = now.get_total_usec() - (self.timeouts.udp_timeout * 1000000)
        max_icmp = now.get_total_usec() - (self.timeouts.icmp_timeout * 1000000)

        # 对话的临时列表
        timedout_convs = []
        for i in list(self.conv_map.keys()):
            is_timedout = False
            conv = self.conv_map[i]
            ip_proto = conv.five_tuple.ip_proto
            if ip_proto == 17:
                is_timedout = (conv.end_ts.get_total_usec() <= max_udp)
            elif ip_proto == 1:
                is_timedout = (conv.end_ts.get_total_usec() <= max_icmp)
            elif ip_proto == 6:
                if conv.state == conversation_state_t.S0 or conv.state == conversation_state_t.S1:
                    is_timedout = (conv.end_ts.get_total_usec() <= max_tcp_syn)
                if conv.state == conversation_state_t.ESTAB:
                    is_timedout = (conv.end_ts.get_total_usec() <= max_tcp_estab)
                if (conv.state == conversation_state_t.REJ or
                        conv.state == conversation_state_t.RSTO or
                        conv.state == conversation_state_t.RSTOS0 or
                        conv.state == conversation_state_t.RSTR):
                    is_timedout = (conv.end_ts.get_total_usec() <= max_tcp_rst)
                if conv.state == conversation_state_t.S2 or conv.state == conversation_state_t.S3:
                    is_timedout = (conv.end_ts.get_total_usec() <= max_tcp_fin)
                if conv.state == conversation_state_t.S2F or conv.state == conversation_state_t.S3F:
                    is_timedout = (conv.end_ts.get_total_usec() <= max_tcp_last_ack)
            if is_timedout:
                timedout_convs.append(conv)
                self.conv_map.pop(i)

        timedout_convs.sort()
        for i in timedout_convs:
            print('timeout')
            self.output_queue.put(i)

    def finish_all_conversations(self):
        self.conv_map.clear()
        # timedout_convs = []
        # for i in list(self.conv_map.keys()):
            # timedout_convs.append(self.conv_map[i])
            # del self.conv_map[i]
        # timedout_convs.sort()
        # for i in timedout_convs:
        #     self.output_queue.put(i)

# 与会话组相关联统计特征
class ConversationFeatures:
    # 声明所有统计特征
    def __init__(self, conv):
        # 与会话相关联
        self.conv = conv
        # 统计当前连接记录与之前2s时间内的连接的关联信息，包含相同目标主机和相同服务两种连接
        self.count = None   # feature 23
        self.srv_count = None # feature 24
        self.serror_rate = None # feature 25
        self.srv_serror_rate = None # feature 26
        self.rerror_rate = None # feature 27
        self.srv_rerror_rate = None # feature 28
        self.same_srv_rate = None # feature 29
        self.diff_srv_rate = None # feature 30
        # 统计当前连接之前100个连接记录中与当前连接具有相同目标主机的统计信息
        self.dst_host_count = None # feature 32
        self.dst_host_srv_count = None # feature 33
        self.dst_host_same_srv_rate = None # feature 34
        self.dst_host_diff_srv_rate = None # feature 35
        self.dst_host_same_src_port_rate = None # feature 36
        self.dst_host_serror_rate = None # feature 38
        self.dst_host_srv_serror_rate = None # feature 39
        self.dst_host_rerror_rate = None # feature 40
        self.dst_host_srv_rerror_rate = None # feature 41
        # 额外的值用来计算特征（31、37）(srv_diff_host_rate/dst_host_srv_diff_host_rate)
        # srv_diff_host_rate = (srv_count - same_srv_count) / srv_count
        self.same_srv_count = None
        self.dst_host_same_srv_count = None

    def get_srv_diff_host_rate(self):  # feature 31
        if self.srv_count == 0:
            return 0.0
        else:
            return (self.srv_count - self.same_srv_count) / self.srv_count

    def get_dst_host_srv_diff_host_rate(self): # feature 37
        if self.dst_host_srv_count == 0:
            return 0.0
        else:
            return (self.dst_host_srv_count - self.dst_host_same_srv_count) / self.dst_host_srv_count

    def get_all_features(self):
        # 基本特征
        fea = self.conv.features()
        # todo 小数位数
        extra_fea = [self.count,self.srv_count,
                     float('%.2f'%self.serror_rate),float('%.2f'%self.srv_serror_rate),float('%.2f'%self.rerror_rate),
                     float('%.2f'%self.srv_rerror_rate),float('%.2f'%self.same_srv_rate),float('%.2f'%self.diff_srv_rate),
                     float('%.2f'%self.get_srv_diff_host_rate()),
                     self.dst_host_count,self.dst_host_srv_count,float('%.2f'%self.dst_host_same_srv_rate),
                     float('%.2f'%self.dst_host_diff_srv_rate),float('%.2f'%self.dst_host_same_src_port_rate),
                     float('%.2f'%self.get_dst_host_srv_diff_host_rate()),float('%.2f'%self.dst_host_serror_rate),
                     float('%.2f'%self.dst_host_srv_serror_rate),float('%.2f'%self.dst_host_rerror_rate),
                     float('%.2f'%self.dst_host_srv_rerror_rate)]
        fea.extend(extra_fea)
        return fea

class FeatureUpdater:
    def set_count(self, cf, count):
        pass
    def set_srv_count(self, cf, srv_count):
        pass
    def set_serror_rate(self, cf, serror_rate):
        pass
    def set_srv_serror_rate(self, cf, srv_serror_rate):
        pass
    def set_rerror_rate(self, cf, rerror_rate):
        pass
    def set_srv_rerror_rate(self, cf, srv_rerror_rate):
        pass
    def set_same_srv_rate(self, cf, same_srv_rate):
        pass
    def set_diff_srv_rate(self, cf, diff_srv_rate):
        pass
    def set_dst_host_same_src_port_rate(self, cf, set_dst_host_same_src_port_rate):
        pass
    def set_same_srv_count(self, cf, same_srv_count):
        pass
# 更新时间窗数据
class FeatureUpdaterTime(FeatureUpdater):
    def set_count(self, cf, count):
        cf.count = count
    def set_srv_count(self, cf, srv_count):
        cf.srv_count = srv_count
    def set_serror_rate(self, cf, serror_rate):
        cf.serror_rate = serror_rate
    def set_srv_serror_rate(self, cf, srv_serror_rate):
        cf.srv_serror_rate = srv_serror_rate
    def set_rerror_rate(self, cf, rerror_rate):
        cf.rerror_rate = rerror_rate
    def set_srv_rerror_rate(self, cf, srv_rerror_rate):
        cf.srv_rerror_rate = srv_rerror_rate
    def set_same_srv_rate(self, cf, same_srv_rate):
        cf.same_srv_rate = same_srv_rate
    def set_diff_srv_rate(self, cf, diff_srv_rate):
        cf.diff_srv_rate = diff_srv_rate
    def set_same_srv_count(self, cf, same_srv_count):
        cf.same_srv_count = same_srv_count

# 更新连接窗数据
class FeatureUpdaterCount(FeatureUpdater):
    def set_count(self, cf, count):
        cf.dst_host_count = count
    def set_srv_count(self, cf, srv_count):
        cf.dst_host_srv_count = srv_count
    def set_serror_rate(self, cf, serror_rate):
        cf.dst_host_serror_rate = serror_rate
    def set_srv_serror_rate(self, cf, srv_serror_rate):
        cf.dst_host_srv_serror_rate = srv_serror_rate
    def set_rerror_rate(self, cf, rerror_rate):
        cf.dst_host_rerror_rate = rerror_rate
    def set_srv_rerror_rate(self, cf, srv_rerror_rate):
        cf.dst_host_srv_rerror_rate = srv_rerror_rate
    def set_same_srv_rate(self, cf, same_srv_rate):
        cf.dst_host_same_srv_rate = same_srv_rate
    def set_diff_srv_rate(self, cf, diff_srv_rate):
        cf.dst_host_diff_srv_rate = diff_srv_rate
    def set_dst_host_same_src_port_rate(self, cf, dst_host_same_src_port_rate):
        cf.dst_host_same_src_port_rate = dst_host_same_src_port_rate
    def set_same_srv_count(self, cf, same_srv_count):
        cf.dst_host_same_srv_count = same_srv_count


# 每台主机的统计数据(IP地址)
class StatsPerHost:
    def __init__(self,feature_updater):
        self.feature_updater = feature_updater
        # 23/32: Number of conversations to same destination IP
        self.count = 0
        # 25/38: Number of conversations that have activated the flag
        self.serror_count = 0
        # 27/40: Number of conversations that have activated the flag REJ among
        self.rerror_count = 0
        # 29/34 : 每个服务的对话个数 (23/32 split by service)
		# 30 可由: diff_srv_rate = (1 - same_srv_rate)
        self.same_srv_count = [0] * conversation_services_t.NUMBER_OF_SERVICES.value

    # 通知统计引擎对话已从窗口移除
    def report_conversation_removal(self, conv):
        self.count -= 1
        # SYN error
        if conv.is_serror():
            self.serror_count -= 1
        # REJ error
        if conv.is_rerror():
            self.rerror_count -= 1
        # 每个服务的conv数量
        service = conv.get_service()
        self.same_srv_count[service.value] -= 1

    #通知统计引擎有新的对话被添加到窗口
    def report_new_conversation(self, cf):
        conv = cf.conv
        service = conv.get_service()
        # 根据窗口中以前的对话设置派生的窗口特性
        # Feature 23/32
        self.feature_updater.set_count(cf, self.count)

        if self.count == 0:
            # Feature 25/38
            self.feature_updater.set_serror_rate(cf, 0.0)
            # Feature 27/40
            self.feature_updater.set_rerror_rate(cf, 0.0)
            # Feature 29/34
            self.feature_updater.set_same_srv_rate(cf, 0.0)
            # Feature 30
            self.feature_updater.set_diff_srv_rate(cf, 0.0)
        else:
            self.feature_updater.set_serror_rate(cf, self.serror_count / self.count)
            self.feature_updater.set_rerror_rate(cf, self.rerror_count / self.count)
            self.feature_updater.set_same_srv_rate(cf, self.same_srv_count[service.value] / self.count)
            self.feature_updater.set_diff_srv_rate(cf, 1.0 - cf.same_srv_rate)
        # Part of feature 31/37
        self.feature_updater.set_same_srv_count(cf, self.same_srv_count[service.value])
        # 包括新的对话到统计
        self.count += 1
        if conv.is_serror():
            self.serror_count += 1
        if conv.is_rerror():
            self.rerror_count += 1
        self.same_srv_count[service.value] += 1

    #检查统计引擎中集合是否为空(例如count == 0)
    def is_empty(self):
        return self.count == 0

# 每个服务的统计数据
class StatsPerService:
    def __init__(self, feature_updater):
        self.feature_updater = feature_updater
        # 24/33: Number of conversations to same service
        self.srv_count = 0
        # 26/39: Number of conversations that have activated the flag
        # S0, S1, S2 or S3 among conv. srv_in count (26/39s)
        self.srv_serror_count = 0
        # 28/41: Number of conversations that have activated the flag REJ among
        # conv. in count (28/41)
        self.srv_rerror_count = 0

    # 通知统计引擎对话已从窗口移除
    def report_conversation_removal(self, conv):
        self.srv_count -= 1
        # SYN error
        if conv.is_serror():
            self.srv_serror_count -= 1
        # REJ error
        if conv.is_rerror():
            self.srv_rerror_count -= 1

    #通知统计引擎有新的对话被添加到窗口
    def report_new_conversation(self, cf):
        # 根据窗口中以前的对话设置派生的窗口特性
        # Feature 24
        self.feature_updater.set_srv_count(cf, self.srv_count)
        conv = cf.conv
        if self.srv_count == 0:
            # Feature 26
            self.feature_updater.set_srv_serror_rate(cf, 0.0)
            # Feature 28
            self.feature_updater.set_srv_rerror_rate(cf, 0.0)
        else:
            self.feature_updater.set_srv_serror_rate(cf, self.srv_serror_count / self.srv_count)
            self.feature_updater.set_srv_rerror_rate(cf, self.srv_rerror_count / self.srv_count)

        # 包括新的对话到统计
        self.srv_count += 1
        if conv.is_serror():
            self.srv_serror_count += 1
        if conv.is_rerror():
            self.srv_rerror_count += 1

    #检查统计引擎中集合是否为空(例如count == 0)
    def is_empty(self):
        return self.srv_count == 0

class StatsPerServiceWithSrcPort(StatsPerService):
    def __init__(self,feature_updater):
        # 每个源端口的会话数
        super(StatsPerServiceWithSrcPort, self).__init__(feature_updater)
        self.same_src_port_counts = {}
    def report_conversation_removal(self, conv):
        super(StatsPerServiceWithSrcPort, self).report_conversation_removal(conv)
        src_port = conv.five_tuple.src_port
        # 找到源端口号和减量的对话计数
        x = self.same_src_port_counts.get(src_port,None)
        if x is not None:
            self.same_src_port_counts[src_port] -= 1
        # 如果给定的src端口没有对话，则从列表中删除
        if self.same_src_port_counts[src_port] == 0:
            del self.same_src_port_counts[src_port]

    def report_new_conversation(self, cf):
        super(StatsPerServiceWithSrcPort, self).report_new_conversation(cf)
        src_port = cf.conv.five_tuple.src_port
        x = self.same_src_port_counts.get(src_port, None)
        if x is not None:
            value = self.same_src_port_counts[src_port]
            self.same_src_port_counts[src_port] += 1
        else:
            self.same_src_port_counts[src_port] = 1
            value = 0
        # Feature 36
        self.feature_updater.set_dst_host_same_src_port_rate(cf, value / self.srv_count)


# 统计窗口
class StatsWindow:
    # 用于保持连接窗口和计算派生特征的抽象模板。
    # 一般的想法是将当前对话的期望值的总和保存在窗口中。
    # 对于新的对话，将添加值。如果对话跳出窗口，它的值将从这些和中减去。
    # 这避免了每次会话都需要遍历整个队列(同时计算其特性)。
    # 执行窗口维护(保持其大小)的算法必须在派生类中指定。
    def __init__(self):
        self.finished_conv = SelfQueue()
        self.per_host = {}
        self.feature_updater = None

    def report_conversation_removal(self, conv):
        dst_ip = conv.five_tuple.dst_ip
        service = conv.get_service()
        #  向上提交 每个主机
        this_host = self.per_host.get(dst_ip, None)
        if this_host is None:
            print('host error')
        this_host.report_conversation_removal(conv)
        # 移除空的
        if this_host.is_empty():
            del self.per_host[dst_ip]
        # 向上提交 每个服务
        self.per_service[service.value].report_conversation_removal(conv)

    def add_conversation(self, cf):
        conv = cf.conv
        dst_ip = conv.five_tuple.dst_ip
        service = conv.get_service()
        this_host = self.per_host.get(dst_ip, None)
        if this_host is None:
            this_host = self.per_host[dst_ip] = StatsPerHost(self.feature_updater)
        this_host.report_new_conversation(cf)
        self.per_service[service.value].report_new_conversation(cf)
        self.finished_conv.put(conv)
        self.perform_window_maintenance(conv)

    def perform_window_maintenance(self, conv):
        # todo override
        pass

# 由时间定义的统计窗口
class StatsWindowTime(StatsWindow):
    def __init__(self, config=None):
        super(StatsWindowTime, self).__init__()
        self.feature_updater = FeatureUpdaterTime()
        self.per_service = [StatsPerService(self.feature_updater)] * conversation_services_t.NUMBER_OF_SERVICES.value
        if config is not None:
            self.window_time_ms = config.time_window_ms
        else:
            self.window_time_ms = 2000
    def perform_window_maintenance(self, conv):
        now = conv.end_ts.get_total_usec()
        max_delete_ts = now - (self.window_time_ms)*1000
        while self.finished_conv.is_empty() and \
            self.finished_conv.front().end_ts.get_total_usec() <= max_delete_ts:
            self.finished_conv.get()
            self.report_conversation_removal(conv)


# 由连接数定义的统计窗口
class StatsWindowCount(StatsWindow):
    def __init__(self, config=None):
        super(StatsWindowCount, self).__init__()
        self.feature_updater = FeatureUpdaterCount()
        self.per_service = [StatsPerServiceWithSrcPort(self.feature_updater)] * conversation_services_t.NUMBER_OF_SERVICES.value
        if config is not None:
            self.window_size = config.count_window_size
        else:
            self.window_size = 100
    # 维持窗口大小
    def perform_window_maintenance(self, conv):
        while self.finished_conv.size() > self.window_size:
            conv = self.finished_conv.get()
            self.report_conversation_removal(conv)

# 统计引擎
class StatEngine:
    # 用于计算派生特征的统计引擎
    def __init__(self, config=None):
        if config is not None:
            self.time_window = StatsWindowTime(config)
            self.count_window = StatsWindowCount(config)
        else:
            conf = Config()
            self.time_window = StatsWindowTime(conf)
            self.count_window = StatsWindowCount(conf)
    # 计算特征，返回特征
    def calculate_features(self, conv):
        #更新两个窗口,返回当前窗口统计特征
        cf = ConversationFeatures(conv)
        self.time_window.add_conversation(cf)
        self.count_window.add_conversation(cf)
        return cf

# 数据包抓取器、pcap读取器
class Sniffer:
    def __init__(self):
        self.reasm = None
        self.stat_engine = None
        self.conv_reconstructor = None
        self.stat_engine = None
        self.asn = None
        self.res_que = None
    # 开始抓取
    def start_cap(self, q, pipe, filter, iface):
        self.reasm = IpReassembler()
        self.stat_engine = StatEngine()
        self.conv_reconstructor = ConversationReconstructor()
        self.res_que = q
        # print(filter)
        # 存在方法 session=TCPSession 暂时不用
        # TODO 保存数据
        # self.asn = sniff(filter=filter, iface=iface, prn=self.extract, store=False)
        self.asn = AsyncSniffer(filter=filter, iface=iface,
                                prn=self.extract, store=False)
        self.asn.start()
        print(pipe.recv())
        self.asn.stop()
        self.conv_reconstructor.finish_all_conversations()
        self.res_que.put(None)
        pipe.close()

    # 开始读取文件 TODO 此功能建议本地使用
    def start_rd(self, file, q=None):
        self.res_que = q
        self.conv_reconstructor = ConversationReconstructor()
        self.stat_engine = StatEngine()
        packets=sniff(offline=file, prn=self.extract)
        # for data in packets:
        #     self.extract(data)


    # 获取下一帧数据
    def next_frame(self, pkg):
        # self.cur += 1
        # if self.cur >= self.all:
        #     return None
        f = IpFragment()
        f.start_ts.set_time(pkg.time * 1000000)
        f.eth_type = pkg.type
        f.five_tuple.src_ip = pkg[IP].src
        f.five_tuple.dst_ip = pkg[IP].dst
        f.five_tuple.ip_proto = pkg[IP].proto
        f.id = pkg[IP].id
        f.ip_flag_mf = (pkg[IP].flags == "MF")
        f.length = pkg[IP].len
        f.ip_frag_offset = pkg[IP].frag
        f.ip_payload_length = f.length - pkg[IP].ihl * 4

        if f.five_tuple.ip_proto == 6 and pkg.haslayer('TCP'):
            f.five_tuple.src_port = pkg[TCP].sport
            f.five_tuple.dst_port = pkg[TCP].dport
            f.tcp_flags = pkg[TCP].flags
        elif f.five_tuple.ip_proto == 17 and pkg.haslayer('UDP'):
            f.five_tuple.src_port = pkg[UDP].sport
            f.five_tuple.dst_port = pkg[UDP].dport
        elif f.five_tuple.ip_proto == 1 and pkg.haslayer('ICMP'):
            f.icmp_code = pkg[ICMP].code
            f.icmp_type = pkg[ICMP].type

        # print(pkg[IP].src)
        # print(pkg[IP].dst)
        # print(pkg[IP].proto)
        f.five_tuple.set_data()
        return f

    # 抽取特征，返回特征
    def extract(self, pkg):
        # pkg.summary()
        frag = self.next_frame(pkg)
        # con.send(frag)
        # frag.show()
        # self.conv_reconstructor.add_packet(pac=frag)
        # 数据包的重组
        now = TimeStamp(frag.start_ts.get_total_usec())
        datagr = None
        datagr = self.reasm.reassemble(fragment=frag)

        # 数据包重组完成，可进行会话构建，否则上报时间
        if datagr is not None:
            self.conv_reconstructor.add_packet(pac=datagr)
        else:
            self.conv_reconstructor.check_timeouts(now=now)

        # 会话构建已完成，进行特征抽取
        while not self.conv_reconstructor.output_queue.is_empty():
            # 获得基本特征
            conv = self.conv_reconstructor.output_queue.get()
            # 获得统计特征
            cf = self.stat_engine.calculate_features(conv)
            # 整合特征，返回特征
            self.res_que.put(cf)
            # print(cf.get_all_features())

if __name__ == "__main__":

    # cf = ConversationFeatures(None)
    # print(cf.conv)
    # cf.count = 1
    # print(cf.count)
    # print(conversation_services_t.SRV_TIM_I == conversation_services_t.SRV_TIM_I)
    sn = Sniffer()
    # sn.start_rd("C:\\Users\\ThinkPad\\Desktop\\ttt.pcap")
    # # sn = AsyncSniffer(filter="icmp", iface='Realtek 8821CE Wireless LAN 802.11ac PCI-E NIC',
    # #                   store=False)
    sn.start_cap('123','123','ip and (tcp or udp or icmp)','Realtek 8821CE Wireless LAN 802.11ac PCI-E NIC')
