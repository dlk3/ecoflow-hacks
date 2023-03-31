# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  MIT License
#
#  Copyright (c) 2022 vwt12eh8
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  https://github.com/vwt12eh8/hassio-ecoflow
#  Combined the contents of __init__.py, receive.py, send.py, and rxtcp.py into
#  one file.
	
from typing import Any, Callable, Iterable, Optional, TypeVar, TypedDict, cast
import datetime
import struct
import logging
import asyncio 

#  Fedora repo does not have ReactiveX, must be installed from pip
import reactivex.operators as ops
from reactivex import Observable, Observer, Subject, compose, throw
from reactivex.subject.replaysubject import ReplaySubject

_LOGGER = logging.getLogger(__name__)

PORT = 8055
PRODUCTS = {
	5: "RIVER",
	7: "RIVER 600 Pro",
	12: "RIVER Pro",
	13: "DELTA Max",
	14: "DELTA Pro",
	15: "DELTA Mini",
	17: "RIVER Mini",
	18: "RIVER Plus",
	20: "Smart Generator",
}

_crc8_tab = [0, 7, 14, 9, 28, 27, 18, 21, 56, 63, 54, 49, 36, 35, 42, 45, 112, 119, 126, 121, 108, 107, 98, 101, 72, 79, 70, 65, 84, 83, 90, 93, 224, 231, 238, 233, 252, 251, 242, 245, 216, 223, 214, 209, 196, 195, 202, 205, 144, 151, 158, 153, 140, 139, 130, 133, 168, 175, 166, 161, 180, 179, 186, 189, 199, 192, 201, 206, 219, 220, 213, 210, 255, 248, 241, 246, 227, 228, 237, 234, 183, 176, 185, 190, 171, 172, 165, 162, 143, 136, 129, 134, 147, 148, 157, 154, 39, 32, 41, 46, 59, 60, 53, 50, 31, 24, 17, 22, 3, 4, 13, 10, 87, 80, 89, 94, 75, 76, 69, 66, 111, 104, 97, 102, 115, 116, 125,
			 122, 137, 142, 135, 128, 149, 146, 155, 156, 177, 182, 191, 184, 173, 170, 163, 164, 249, 254, 247, 240, 229, 226, 235, 236, 193, 198, 207, 200, 221, 218, 211, 212, 105, 110, 103, 96, 117, 114, 123, 124, 81, 86, 95, 88, 77, 74, 67, 68, 25, 30, 23, 16, 5, 2, 11, 12, 33, 38, 47, 40, 61, 58, 51, 52, 78, 73, 64, 71, 82, 85, 92, 91, 118, 113, 120, 127, 106, 109, 100, 99, 62, 57, 48, 55, 34, 37, 44, 43, 6, 1, 8, 15, 26, 29, 20, 19, 174, 169, 160, 167, 178, 181, 188, 187, 150, 145, 152, 159, 138, 141, 132, 131, 222, 217, 208, 215, 194, 197, 204, 203, 230, 225, 232, 239, 250, 253, 244, 243]
_crc16_tab = [0, 49345, 49537, 320, 49921, 960, 640, 49729, 50689, 1728, 1920, 51009, 1280, 50625, 50305, 1088, 52225, 3264, 3456, 52545, 3840, 53185, 52865, 3648, 2560, 51905, 52097, 2880, 51457, 2496, 2176, 51265, 55297, 6336, 6528, 55617, 6912, 56257, 55937, 6720, 7680, 57025, 57217, 8000, 56577, 7616, 7296, 56385, 5120, 54465, 54657, 5440, 55041, 6080, 5760, 54849, 53761, 4800, 4992, 54081, 4352, 53697, 53377, 4160, 61441, 12480, 12672, 61761, 13056, 62401, 62081, 12864, 13824, 63169, 63361, 14144, 62721, 13760, 13440, 62529, 15360, 64705, 64897, 15680, 65281, 16320, 16000, 65089, 64001, 15040, 15232, 64321, 14592, 63937, 63617, 14400, 10240, 59585, 59777, 10560, 60161, 11200, 10880, 59969, 60929, 11968, 12160, 61249, 11520, 60865, 60545, 11328, 58369, 9408, 9600, 58689, 9984, 59329, 59009, 9792, 8704, 58049, 58241, 9024, 57601, 8640, 8320, 57409, 40961, 24768,
			  24960, 41281, 25344, 41921, 41601, 25152, 26112, 42689, 42881, 26432, 42241, 26048, 25728, 42049, 27648, 44225, 44417, 27968, 44801, 28608, 28288, 44609, 43521, 27328, 27520, 43841, 26880, 43457, 43137, 26688, 30720, 47297, 47489, 31040, 47873, 31680, 31360, 47681, 48641, 32448, 32640, 48961, 32000, 48577, 48257, 31808, 46081, 29888, 30080, 46401, 30464, 47041, 46721, 30272, 29184, 45761, 45953, 29504, 45313, 29120, 28800, 45121, 20480, 37057, 37249, 20800, 37633, 21440, 21120, 37441, 38401, 22208, 22400, 38721, 21760, 38337, 38017, 21568, 39937, 23744, 23936, 40257, 24320, 40897, 40577, 24128, 23040, 39617, 39809, 23360, 39169, 22976, 22656, 38977, 34817, 18624, 18816, 35137, 19200, 35777, 35457, 19008, 19968, 36545, 36737, 20288, 36097, 19904, 19584, 35905, 17408, 33985, 34177, 17728, 34561, 18368, 18048, 34369, 33281, 17088, 17280, 33601, 16640, 33217, 32897, 16448]

NO_USB_SWITCH = {5, 7, 12, 14, 15, 18}

class RxTcpAutoConnection:
	__rx = None
	__tx = None

	def __init__(self, host: str, port: int):
		self.host = host
		self.port = port
		self.received = Subject[Optional[bytes]]()
		self.__is_open = True
		self.__task = asyncio.create_task(self.__loop())
		self.__opened = asyncio.Future()

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc, tb):
		self.close()
		await self.wait_closed()

	def close(self):
		self.__is_open = False
		if self.__rx:
			self.__rx.feed_eof()

	async def drain(self):
		await self.__tx.drain()

	def reconnect(self):
		if self.__rx:
			self.__rx.feed_eof()

	async def wait_closed(self):
		try:
			await self.__task
		except:
			pass
		try:
			await self.__tx.wait_closed()
		except:
			pass

	async def wait_opened(self):
		await self.__opened

	def write(self, data: bytes):
		self.__tx.write(data)

	async def __loop(self):
		while self.__is_open:
			_LOGGER.debug(f"connecting {self.host}")
			try:
				(self.__rx, self.__tx) = await asyncio.open_connection(self.host, self.port)
			except Exception as ex:
				_LOGGER.debug(ex)
				await asyncio.sleep(1)
				continue
			_LOGGER.debug(f"connected {self.host}")
			if not self.__opened.done():
				self.__opened.set_result(None)
			try:
				while not self.__rx.at_eof():
					data = await self.__rx.read(1024)
					_LOGGER.debug(data)
					if data:
						self.received.on_next(data)
			except Exception as ex:
				if type(ex) is not TimeoutError:
					_LOGGER.exception(ex)
			except BaseException as ex:
				self.received.on_error(ex)
				return
			finally:
				self.__rx.feed_eof()
				self.__tx.close()
			self.received.on_next(None)
		self.received.on_completed()
		
class EcoFlowClient:
	__disconnected = None
	__extra_connected = False

	def __init__(self, product_name, addr, timeout):
		self.tcp = RxTcpAutoConnection(addr, PORT)
		self.product: int = list(PRODUCTS.keys())[list(PRODUCTS.values()).index(product_name)]
		self.diagnostics = dict[str, dict[str, Any]]()

		self.device_info_main={}
		self.device_info_main["manufacturer"] = "EcoFlow"

		self.received = self.tcp.received.pipe(
			merge_packet(),
			ops.map(decode_packet),
			ops.share(),
		)
		self.pd = self.received.pipe(
			ops.filter(is_pd),
			ops.map(lambda x: parse_pd(x[3], self.product)),
			ops.multicast(subject=ReplaySubject(1, timeout)),
			ops.ref_count(),
		)
		self.ems = self.received.pipe(
			ops.filter(is_ems),
			ops.map(lambda x: parse_ems(x[3], self.product)),
			ops.multicast(subject=ReplaySubject(1, timeout)),
			ops.ref_count(),
		)
		self.inverter = self.received.pipe(
			ops.filter(is_inverter),
			ops.map(lambda x: parse_inverter(x[3], self.product)),
			ops.multicast(subject=ReplaySubject(1, timeout)),
			ops.ref_count(),
		)
		self.mppt = self.received.pipe(
			ops.filter(is_mppt),
			ops.map(lambda x: parse_mppt(x[3], self.product)),
			ops.multicast(subject=ReplaySubject(1, timeout)),
			ops.ref_count(),
		)
		self.bms = self.received.pipe(
			ops.filter(is_bms),
			ops.map(lambda x: parse_bms(x[3], self.product)),
			ops.multicast(subject=ReplaySubject(1, timeout)),
			ops.ref_count(),
		)

		self.dc_in_current_config = self.received.pipe(
			ops.filter(is_dc_in_current_config),
			ops.map(lambda x: parse_dc_in_current_config(x[3])),
		)
		self.dc_in_type = self.received.pipe(
			ops.filter(is_dc_in_type),
			ops.map(lambda x: parse_dc_in_type(x[3])),
		)
		self.fan_auto = self.received.pipe(
			ops.filter(is_fan_auto),
			ops.map(lambda x: parse_fan_auto(x[3])),
		)
		self.lcd_timeout = self.received.pipe(
			ops.filter(is_lcd_timeout),
			ops.map(lambda x: parse_lcd_timeout(x[3])),
		)

		self.disconnected = Subject[Optional[int]]()

		def _disconnected(*args):
			self.__disconnected = None
			self.tcp.reconnect()
			self.diagnostics.clear()
			self.disconnected.on_next(None)
			if self.__extra_connected:
				self.__extra_connected = False

		def reset_timer(*args):
			if self.__disconnected:
				self.__disconnected()

		def end_timer(ex=None):
			self.disconnected.on_next(None)
			if ex:
				self.disconnected.on_error(ex)
			else:
				self.disconnected.on_completed()
		self.received.subscribe(reset_timer, end_timer, end_timer)

		def pd_updated(data: dict[str, Any]):
			self.diagnostics["pd"] = data
			self.device_info_main["model"] = get_model_name(
				self.product, data["model"])
			if self.__extra_connected != has_extra(self.product, data.get("model", None)):
				self.__extra_connected = not self.__extra_connected
				if not self.__extra_connected:
					self.disconnected.on_next(1)
		self.pd.subscribe(pd_updated)

		def bms_updated(data: tuple[int, dict[str, Any]]):
			if "bms" not in self.diagnostics:
				self.diagnostics["bms"] = dict[str, Any]()
			self.diagnostics["bms"][data[0]] = data[1]
		self.bms.subscribe(bms_updated)

		def ems_updated(data: dict[str, Any]):
			self.diagnostics["ems"] = data
		self.ems.subscribe(ems_updated)

		def inverter_updated(data: dict[str, Any]):
			self.diagnostics["inverter"] = data
		self.inverter.subscribe(inverter_updated)

		def mppt_updated(data: dict[str, Any]):
			self.diagnostics["mppt"] = data
		self.mppt.subscribe(mppt_updated)

	async def close(self):
		self.tcp.close()
		await self.tcp.wait_closed()

class Serial(TypedDict):
	chk_val: int
	product: int
	product_detail: int
	model: int
	serial: str
	cpu_id: str

def _merge_packet(obs: Observable[Optional[bytes]]):
	def func(sub: Observer[bytes], sched=None):
		x = b''

		def next(rcv: Optional[bytes]):
			nonlocal x
			if rcv is None:
				x = b''
				return
			x += rcv
			while len(x) >= 18:
				if x[:2] != b'\xaa\x02':
					x = x[1:]
					continue
				size = int.from_bytes(x[2:4], 'little')
				if 18 + size > len(x):
					return
				if calcCrc8(x[:4]) != x[4:5]:
					x = x[2:]
					continue
				if calcCrc16(x[:16 + size]) != x[16 + size:18 + size]:
					x = x[2:]
					continue
				sub.on_next(x[:18 + size])
				x = x[18 + size:]

		return obs.subscribe(next, sub.on_error, sub.on_completed, scheduler=sched)

	return Observable[bytes](func)


def _parse_dict(d: bytes, types: Iterable[tuple[str, int, Callable[[bytes], Any]]]):
	res = dict[str, Any]()
	idx = 0
	_len = len(d)
	for (name, size, fn) in types:
		if name is not None:
			res[name] = fn(d[idx:idx + size])
		idx += size
		if idx >= _len:
			break
	return res


def _to_float(d: bytes) -> float:
	return struct.unpack("<f", d)[0]


def _to_int(d: bytes):
	return int.from_bytes(d, "little")


def _to_int_ex(div: int = 1):
	def f(d: bytes):
		v = _to_int(d)
		if v is None:
			return None
		v /= div
		return v
	return f


def _to_timedelta_min(d: bytes):
	return str(datetime.timedelta(minutes=int.from_bytes(d, "little")))


def _to_timedelta_sec(d: bytes):
	return str(datetime.timedelta(seconds=int.from_bytes(d, "little")))


def _to_utf8(d: bytes):
	try:
		return d.decode("utf-8")
	except:
		return None


def _to_ver(data: Iterable[int]):
	return ".".join(str(i) for i in data)


def _to_ver_reversed(data: Iterable[int]):
	return _to_ver(reversed(data))


def decode_packet(x: bytes):
	size = int.from_bytes(x[2:4], 'little')
	args = x[16:16 + size]
	if ((x[5] >> 5) & 3) == 1:
		# Deobfuscation
		args = bytes(v ^ x[6] for v in args)
	return (x[12], x[14], x[15], args)


def is_bms(x: tuple[int, int, int]):
	return x[0:3] == (3, 32, 50) or x[0:3] == (6, 32, 2) or x[0:3] == (6, 32, 50)


def is_dc_in_current_config(x: tuple[int, int, int]):
	return x[0:3] == (4, 32, 72) or x[0:3] == (5, 32, 72)


def is_dc_in_type(x: tuple[int, int, int]):
	return x[0:3] == (4, 32, 68) or x[0:3] == (5, 32, 82)


def is_ems(x: tuple[int, int, int]):
	return x[0:3] == (3, 32, 2)


def is_fan_auto(x: tuple[int, int, int]):
	return x[0:3] == (4, 32, 74)


def is_inverter(x: tuple[int, int, int]):
	return x[0:3] == (4, 32, 2)


def is_lcd_timeout(x: tuple[int, int, int]):
	return x[0:3] == (2, 32, 40)


def is_mppt(x: tuple[int, int, int]):
	return x[0:3] == (5, 32, 2)


def is_pd(x: tuple[int, int, int]):
	return x[0:3] == (2, 32, 2)


def is_serial_main(x: tuple[int, int, int]):
	return x[0] in [2, 11] and x[1:3] == (1, 65)


def is_serial_extra(x: tuple[int, int, int]):
	return x[0:3] == (6, 1, 65)


def parse_bms(d: bytes, product: int):
	if is_delta(product):
		return parse_bms_delta(d)
	if is_river(product):
		return parse_bms_river(d)
	return (0, {})


def parse_bms_delta(d: bytes):
	val = _parse_dict(d, [
		("num", 1, _to_int),
		("battery_type", 1, _to_int),
		("battery_cell_id", 1, _to_int),
		("battery_error", 4, _to_int),
		("battery_version", 4, _to_ver_reversed),
		("battery_level", 1, _to_int),
		("battery_voltage", 4, _to_int_ex(div=1000)),
		("battery_current", 4, _to_int),
		("battery_temp", 1, _to_int),
		("_open_bms_idx", 1, _to_int),
		("battery_capacity_design", 4, _to_int),
		("battery_capacity_remain", 4, _to_int),
		("battery_capacity_full", 4, _to_int),
		("battery_cycles", 4, _to_int),
		("_soh", 1, _to_int),
		("battery_voltage_max", 2, _to_int_ex(div=1000)),
		("battery_voltage_min", 2, _to_int_ex(div=1000)),
		("battery_temp_max", 1, _to_int),
		("battery_temp_min", 1, _to_int),
		("battery_mos_temp_max", 1, _to_int),
		("battery_mos_temp_min", 1, _to_int),
		("battery_fault", 1, _to_int),
		("_sys_stat_reg", 1, _to_int),
		("_tag_chg_current", 4, _to_int),
		("battery_level_f32", 4, _to_float),
		("battery_in_power", 4, _to_int),
		("battery_out_power", 4, _to_int),
		("battery_remain", 4, _to_timedelta_min),
	])
	return (cast(int, val.pop("num")), val)


def parse_bms_river(d: bytes):
	return (1, _parse_dict(d, [
		("battery_error", 4, _to_int),
		("battery_version", 4, _to_ver_reversed),
		("battery_level", 1, _to_int),
		("battery_voltage", 4, _to_int_ex(div=1000)),
		("battery_current", 4, _to_int),
		("battery_temp", 1, _to_int),
		("battery_capacity_remain", 4, _to_int),
		("battery_capacity_full", 4, _to_int),
		("battery_cycles", 4, _to_int),
		("ambient_mode", 1, _to_int),
		("ambient_animate", 1, _to_int),
		("ambient_color", 4, list),
		("ambient_brightness", 1, _to_int),
	]))


def parse_dc_in_current_config(d: bytes):
	return int.from_bytes(d[:4], "little")


def parse_dc_in_type(d: bytes):
	return d[1]


def parse_ems(d: bytes, product: int):
	if is_delta(product):
		return parse_ems_delta(d)
	if is_river(product):
		return parse_ems_river(d)
	# if is_river_mini(product):
	#     return parse_ems_river_mini(d)
	return {}


def parse_ems_delta(d: bytes):
	return _parse_dict(d, [
		("_state_charge", 1, _to_int),
		("_chg_cmd", 1, _to_int),
		("_dsg_cmd", 1, _to_int),
		("battery_main_voltage", 4, _to_int_ex(div=1000)),
		("battery_main_current", 4, _to_int_ex(div=1000)),
		("_fan_level", 1, _to_int),
		("battery_level_max", 1, _to_int),
		("model", 1, _to_int),
		("battery_main_level", 1, _to_int),
		("_flag_open_ups", 1, _to_int),
		("battery_main_warning", 1, _to_int),
		("battery_remain_charge", 4, _to_timedelta_min),
		("battery_remain_discharge", 4, _to_timedelta_min),
		("battery_main_normal", 1, _to_int),
		("battery_main_level_f32", 4, _to_float),
		("_is_connect", 3, _to_int),
		("_max_available_num", 1, _to_int),
		("_open_bms_idx", 1, _to_int),
		("battery_main_voltage_min", 4, _to_int_ex(div=1000)),
		("battery_main_voltage_max", 4, _to_int_ex(div=1000)),
		("battery_level_min", 1, _to_int),
		("generator_level_start", 1, _to_int),
		("generator_level_stop", 1, _to_int),
	])


def parse_ems_river(d: bytes):
	return _parse_dict(d, [
		("battery_main_error", 4, _to_int),
		("battery_main_version", 4, _to_ver_reversed),
		("battery_main_level", 1, _to_int),
		("battery_main_voltage", 4, _to_int_ex(div=1000)),
		("battery_main_current", 4, _to_int),
		("battery_main_temp", 1, _to_int),
		("_open_bms_idx", 1, _to_int),
		("battery_capacity_remain", 4, _to_int),
		("battery_capacity_full", 4, _to_int),
		("battery_cycles", 4, _to_int),
		("battery_level_max", 1, _to_int),
		("battery_main_voltage_max", 2, _to_int_ex(div=1000)),
		("battery_main_voltage_min", 2, _to_int_ex(div=1000)),
		("battery_main_temp_max", 1, _to_int),
		("battery_main_temp_min", 1, _to_int),
		("mos_temp_max", 1, _to_int),
		("mos_temp_min", 1, _to_int),
		("battery_main_fault", 1, _to_int),
		("_bq_sys_stat_reg", 1, _to_int),
		("_tag_chg_amp", 4, _to_int),
	])


# def parse_ems_river_mini(d: bytes):
#     pass

def parse_fan_auto(d: bytes):
	return d[0] == 1


def parse_inverter(d: bytes, product: int):
	if is_delta(product):
		return parse_inverter_delta(d)
	if is_river(product):
		return parse_inverter_river(d)
	# if is_river_mini(product):
	#     return parse_pd_river_mini(d)
	return {}


def parse_inverter_delta(d: bytes):
	return _parse_dict(d, [
		("ac_error", 4, _to_int),
		("ac_version", 4, _to_ver_reversed),
		("ac_in_type", 1, _to_int),
		("ac_in_power", 2, _to_int),
		("ac_out_power", 2, _to_int),
		("ac_type", 1, _to_int),
		("ac_out_voltage", 4, _to_int_ex(div=1000)),
		("ac_out_current", 4, _to_int_ex(div=1000)),
		("ac_out_freq", 1, _to_int),
		("ac_in_voltage", 4, _to_int_ex(div=1000)),
		("ac_in_current", 4, _to_int_ex(div=1000)),
		("ac_in_freq", 1, _to_int),
		("ac_out_temp", 2, _to_int),
		("dc_in_voltage", 4, _to_int),
		("dc_in_current", 4, _to_int),
		("ac_in_temp", 2, _to_int),
		("fan_state", 1, _to_int),
		("ac_out_state", 1, _to_int),
		("ac_out_xboost", 1, _to_int),
		("ac_out_voltage_config", 4, _to_int_ex(div=1000)),
		("ac_out_freq_config", 1, _to_int),
		("fan_config", 1, _to_int),
		("ac_in_pause", 1, _to_int),
		("ac_in_limit_switch", 1, _to_int),
		("ac_in_limit_max", 2, _to_int),
		("ac_in_limit_custom", 2, _to_int),
		("ac_out_timeout", 2, _to_int),
	])


def parse_inverter_river(d: bytes):
	return _parse_dict(d, [
		("ac_error", 4, _to_int),
		("ac_version", 4, _to_ver_reversed),
		("in_type", 1, _to_int),
		("in_power", 2, _to_int),
		("ac_out_power", 2, _to_int),
		("ac_type", 1, _to_int),
		("ac_out_voltage", 4, _to_int_ex(div=1000)),
		("ac_out_current", 4, _to_int_ex(div=1000)),
		("ac_out_freq", 1, _to_int),
		("ac_in_voltage", 4, _to_int_ex(div=1000)),
		("ac_in_current", 4, _to_int_ex(div=1000)),
		("ac_in_freq", 1, _to_int),
		("ac_out_temp", 1, _to_int),
		("dc_in_voltage", 4, _to_int_ex(div=1000)),
		("dc_in_current", 4, _to_int_ex(div=1000)),
		("ac_in_temp", 1, _to_int),
		("fan_state", 1, _to_int),
		("ac_out_state", 1, _to_int),
		("ac_out_xboost", 1, _to_int),
		("ac_out_voltage_config", 4, _to_int_ex(div=1000)),
		("ac_out_freq_config", 1, _to_int),
		("ac_in_slow", 1, _to_int),
		("ac_out_timeout", 2, _to_int),
		("fan_config", 1, _to_int),
	])


def parse_lcd_timeout(d: bytes):
	return int.from_bytes(d[1:3], "little")


def parse_mppt(d: bytes, product: int):
	if is_delta(product):
		return parse_mppt_delta(d)
	return {}


def parse_mppt_delta(d: bytes):
	return _parse_dict(d, [
		("dc_in_error", 4, _to_int),
		("dc_in_version", 4, _to_ver_reversed),
		("dc_in_voltage", 4, _to_int_ex(div=10)),
		("dc_in_current", 4, _to_int_ex(div=100)),
		("dc_in_power", 2, _to_int_ex(div=10)),
		("_volt_?_out", 4, _to_int),
		("_curr_?_out", 4, _to_int),
		("_watts_?_out", 2, _to_int),
		("dc_in_temp", 2, _to_int),
		("dc_in_type", 1, _to_int),
		("dc_in_type_config", 1, _to_int),
		("_dc_in_type", 1, _to_int),
		("dc_in_state", 1, _to_int),
		("anderson_out_voltage", 4, _to_int),
		("anderson_out_current", 4, _to_int),
		("anderson_out_power", 2, _to_int),
		("car_out_voltage", 4, _to_int_ex(div=10)),
		("car_out_current", 4, _to_int_ex(div=100)),
		("car_out_power", 2, _to_int_ex(div=10)),
		("car_out_temp", 2, _to_int),
		("car_out_state", 1, _to_int),
		("dc24_temp", 2, _to_int),
		("dc24_state", 1, _to_int),
		("dc_in_pause", 1, _to_int),
		("_dc_in_switch", 1, _to_int),
		("_dc_in_limit_max", 2, _to_int),
		("_dc_in_limit_custom", 2, _to_int),
	])


def parse_pd(d: bytes, product: int):
	if is_delta(product):
		return parse_pd_delta(d)
	if is_river(product):
		return parse_pd_river(d)
	# if is_river_mini(product):
	#     return parse_pd_river_mini(d)
	return {}


def parse_pd_delta(d: bytes):
	return _parse_dict(d, [
		("model", 1, _to_int),
		("pd_error", 4, _to_int),
		("pd_version", 4, _to_ver_reversed),
		("wifi_version", 4, _to_ver_reversed),
		("wifi_autorecovery", 1, _to_int),
		("battery_level", 1, _to_int),
		("out_power", 2, _to_int),
		("in_power", 2, _to_int),
		("remain_display", 4, _to_timedelta_min),
		("beep", 1, _to_int),
		("_watts_anderson_out", 1, _to_int),
		("usb_out1_power", 1, _to_int),
		("usb_out2_power", 1, _to_int),
		("usbqc_out1_power", 1, _to_int),
		("usbqc_out2_power", 1, _to_int),
		("typec_out1_power", 1, _to_int),
		("typec_out2_power", 1, _to_int),
		("typec_out1_temp", 1, _to_int),
		("typec_out2_temp", 1, _to_int),
		("car_out_state", 1, _to_int),
		("car_out_power", 1, _to_int),
		("car_out_temp", 1, _to_int),
		("standby_timeout", 2, _to_int),
		("lcd_timeout", 2, _to_int),
		("lcd_brightness", 1, _to_int),
		("car_in_energy", 4, _to_int),
		("mppt_in_energy", 4, _to_int),
		("ac_in_energy", 4, _to_int),
		("car_out_energy", 4, _to_int),
		("ac_out_energy", 4, _to_int),
		("usb_time", 4, _to_timedelta_sec),
		("typec_time", 4, _to_timedelta_sec),
		("car_out_time", 4, _to_timedelta_sec),
		("ac_out_time", 4, _to_timedelta_sec),
		("ac_in_time", 4, _to_timedelta_sec),
		("car_in_time", 4, _to_timedelta_sec),
		("mppt_time", 4, _to_timedelta_sec),
		(None, 2, None),
		("_ext_rj45", 1, _to_int),
		("_ext_infinity", 1, _to_int),
	])


def parse_pd_river(d: bytes):
	return _parse_dict(d, [
		("model", 1, _to_int),
		("pd_error", 4, _to_int),
		("pd_version", 4, _to_ver_reversed),
		("battery_level", 1, _to_int),
		("out_power", 2, _to_int),
		("in_power", 2, _to_int),
		("remain_display", 4, _to_timedelta_min),
		("car_out_state", 1, _to_int),
		("light_state", 1, _to_int),
		("beep", 1, _to_int),
		("typec_out1_power", 1, _to_int),
		("usb_out1_power", 1, _to_int),
		("usb_out2_power", 1, _to_int),
		("usbqc_out1_power", 1, _to_int),
		("car_out_power", 1, _to_int),
		("light_power", 1, _to_int),
		("typec_out1_temp", 1, _to_int),
		("car_out_temp", 1, _to_int),
		("standby_timeout", 2, _to_int),
		("car_in_energy", 4, _to_int),
		("mppt_in_energy", 4, _to_int),
		("ac_in_energy", 4, _to_int),
		("car_out_energy", 4, _to_int),
		("ac_out_energy", 4, _to_int),
		("usb_time", 4, _to_timedelta_sec),
		("usbqc_time", 4, _to_timedelta_sec),
		("typec_time", 4, _to_timedelta_sec),
		("car_out_time", 4, _to_timedelta_sec),
		("ac_out_time", 4, _to_timedelta_sec),
		("car_in_time", 4, _to_timedelta_sec),
		("mppt_time", 4, _to_timedelta_sec),
	])


# def parse_pd_river_mini(d: bytes):
#     return _parse_dict(d, [
#         ("model", 1, _to_int),
#         ("pd_error", 4, _to_int),
#         ("pd_version", 4, _to_ver_reversed),
#         ("wifi_version", 4, _to_ver_reversed),
#         ("wifi_autorecovery", 1,),
#         ("soc_sum", 1, _to_int),
#         ("watts_out_sum", 2, _to_int),
#         ("watts_in_sum", 2, _to_int),
#         ("remain_time", 4, _to_int),
#         ("beep", 1, _to_int),
#         ("dc_out", 1, _to_int),
#         ("usb1_watts", 1, _to_int),
#         ("usb2_watts", 1, _to_int),
#         ("usbqc1_watts", 1, _to_int),
#         ("usbqc2_watts", 1, _to_int),
#         ("typec1_watts", 1, _to_int),
#         ("typec2_watts", 1, _to_int),
#         ("typec1_temp", 1, _to_int),
#         ("typec2_temp", 1, _to_int),
#         ("dc_out_watts", 1, _to_int),
#         ("car_out_temp", 1, _to_int),
#         ("standby_timeout", 2, _to_int),
#         ("lcd_sec", 2, _to_int),
#         ("lcd_brightness", 1, _to_int),
#         ("chg_power_dc", 4, _to_int),
#         ("chg_power_mppt", 4, _to_int),
#         ("chg_power_ac", 4, _to_int),
#         ("dsg_power_dc", 4, _to_int),
#         ("dsg_power_ac", 4, _to_int),
#         ("usb_used_time", 4, _to_int),
#         ("usbqc_used_time", 4, _to_int),
#         ("typec_used_time", 4, _to_int),
#         ("dc_out_used_time", 4, _to_int),
#         ("ac_out_used_time", 4, _to_int),
#         ("dc_in_used_time", 4, _to_int),
#         ("mppt_used_time", 4, _to_int),
#         (None, 5, None),
#         ("sys_chg_flag", 1, _to_int),
#         ("wifi_rssi", 1, _to_int),
#         ("wifi_watts", 1, _to_int),
#     ])


def parse_serial(d: bytes) -> Serial:
	return _parse_dict(d, [
		("chk_val", 4, _to_int),
		("product", 1, _to_int),
		(None, 1, None),
		("product_detail", 1, _to_int),
		("model", 1, _to_int),
		("serial", 15, _to_utf8),
		(None, 1, None),
		("cpu_id", 12, _to_utf8),
	])


def merge_packet():
	return _merge_packet


def calcCrc8(data: bytes):
	crc = 0
	for i3 in range(len(data)):
		crc = _crc8_tab[(crc ^ data[i3]) & 255]
	return crc.to_bytes(1, "little")


def calcCrc16(data: bytes):
	crc = 0
	for i3 in range(len(data)):
		crc = _crc16_tab[(crc ^ data[i3]) & 255] ^ (crc >> 8)
	return crc.to_bytes(2, "little")


def get_model_name(product: int, model: int):
	if product == 5 and model == 2:
		return "RIVER Max"
	elif product == 18 and model == 2:
		return "RIVER Max Plus"
	else:
		return PRODUCTS.get(product, None)


def has_extra(product: int, model: int):
	if product in [5, 12]:
		return model == 2
	return False


def has_light(product: int):
	return product in [5, 7, 12, 18]


def is_delta(product: int):
	return 12 < product < 16


def is_delta_max(product: int):
	return product == 13


def is_delta_mini(product: int):
	return product == 15


def is_delta_pro(product: int):
	return product == 14


def is_power_station(product: int):
	return is_delta(product) or is_river(product) or is_river_mini(product)


def is_river(product: int):
	return product in [5, 7, 12, 18]


def is_river_mini(product: int):
	return product == 17

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  send.py
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def _btoi(b: Optional[bool]):
    if b is None:
        return 255
    return 1 if b else 0


def build2(dst: int, cmd_set: int, cmd_id: int, data: bytes = b''):
    b = bytes([170, 2])
    b += len(data).to_bytes(2, "little")
    b += calcCrc8(b)
    b += bytes([13, 0, 0, 0, 0, 0, 0, 32, dst, cmd_set, cmd_id])
    b += data
    b += calcCrc16(b)
    return b


def get_product_info(dst: int):
    return build2(dst, 1, 5)


def get_cpu_id():
    return build2(2, 1, 64)


def get_serial_main():
    return build2(2, 1, 65)


def get_pd():
    return build2(2, 32, 2, b'\0')


def reset():
    return build2(2, 32, 3)


def set_standby_timeout(value: int):
    return build2(2, 32, 33, value.to_bytes(2, "little"))


def set_usb(enable: bool):
    return build2(2, 32, 34, bytes([1 if enable else 0]))


def set_light(product: int, value: int):
    return build2(2, 32, 35, bytes([value]))


def set_dc_out(product: int, enable: bool):
    if is_delta(product):
        cmd = (5, 32, 81)
    elif product == 20:
        cmd = (8, 8, 3)
    elif product in [5, 7, 12, 18]:
        cmd = (2, 32, 34)
    else:
        cmd = (2, 32, 37)
    return build2(*cmd, bytes([1 if enable else 0]))


def set_beep(enable: bool):
    return build2(2, 32, 38, bytes([0 if enable else 1]))


def set_lcd(product: int, time: int = 0xFFFF, light: int = 255):
    arg = time.to_bytes(2, "little")
    if is_delta(product) or is_river_mini(product):
        arg += bytes([light])
    return build2(2, 32, 39, arg)


def get_lcd():
    return build2(2, 32, 40)


def close(value: int):
    return build2(2, 32, 41, value.to_bytes(2, "little"))


def get_ems_main():
    return build2(3, 32, 2)


def set_level_max(product: int, value: int):
    dst = 4 if product == 17 else 3
    return build2(dst, 32, 49, bytes([value]))


def set_level_min(value: int):
    return build2(3, 32, 51, bytes([value]))


def set_generate_start(value: int):
    return build2(3, 32, 52, bytes([value]))


def set_generate_stop(value: int):
    return build2(3, 32, 53, bytes([value]))


def get_inverter():
    return build2(4, 32, 2)


def set_ac_in_slow(value: bool):
    return build2(4, 32, 65, bytes([_btoi(value)]))


def set_ac_out(product: int, enable: bool = None, xboost: bool = None, freq: int = 255):
    if product == 20:
        cmd = (8, 8, 2)
        arg = [_btoi(enable)]
    else:
        cmd = (4, 32, 66)
        arg = [_btoi(enable), _btoi(xboost), 255, 255, 255, 255, freq]
    return build2(*cmd, bytes(arg))


def set_dc_in_type(product: int, value: int):
    if is_delta(product):
        cmd = (5, 32, 82)
    else:
        cmd = (4, 32, 67)
    return build2(*cmd, bytes([value]))


def get_dc_in_type(product: int):
    if is_delta(product):
        cmd = (5, 32, 82)
    else:
        cmd = (4, 32, 68)
    return build2(*cmd, bytes([0]))


def set_ac_in_limit(watts: int = 0xFFFF, pause: bool = None):
    arg = bytes([255, 255])
    arg += watts.to_bytes(2, "little")
    arg += bytes([_btoi(pause)])
    return build2(4, 32, 69, arg)


def set_dc_in_current(product: int, value: int):
    dst = 5 if is_delta(product) else 4
    return build2(dst, 32, 71, value.to_bytes(4, "little"))


def get_dc_in_current(product: int):
    dst = 5 if is_delta(product) else 4
    return build2(dst, 32, 72)


def set_fan_auto(product: int, value: bool):
    return build2(4, 32, 73, bytes([1 if value else 3]))


def get_fan_auto():
    return build2(4, 32, 74)


def get_lab():
    return build2(4, 32, 84)


def set_lab(value: int):
    return build2(4, 32, 84, bytes([value]))


def set_ac_timeout(value: int):
    return build2(4, 32, 153, value.to_bytes(2, "little"))


def get_serial_extra():
    return build2(6, 1, 65)


def get_ems_extra():
    return build2(6, 32, 2)


def set_ambient(mode: int = 255, animate: int = 255, color=(255, 255, 255, 255), brightness=255):
    arg = [mode, animate, *color, brightness]
    return build2(6, 32, 97, bytes(arg))


def _set_watt(value: int):
    return build2(8, 8, 7, value.to_bytes(2, "little"))
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#  Get a JSON array of system information
async def _get_status(product_name, ip_address, timeout_seconds):
	try:
		timeout = datetime.timedelta(seconds=timeout_seconds)
		client =  EcoFlowClient(product_name, ip_address, timeout)
		await asyncio.sleep(5)
		#while "pd" not in client.diagnostics or "ems" not in client.diagnostics or "bms" not in client.diagnostics or "inverter" not in client.diagnostics or "mppt" not in client.diagnostics :
		#	print('waiting')
		#	await asyncio.sleep(0)
		return client.diagnostics
	finally:
		if client:
			await client.close()

def get_status(product_name, ip_address, timeout_seconds):
	return asyncio.run(_get_status(product_name, ip_address, timeout_seconds))

#  Send one of the get/set commands from the "send.py" portion of the API
async def _set_config(product_name, ip_address, timeout_seconds, parameter):
	try:
		timeout = datetime.timedelta(seconds=timeout_seconds)
		client =  EcoFlowClient(product_name, ip_address, timeout)
		while not client.diagnostics:
			await asyncio.sleep(0)
		return client.tcp.write(parameter)
	finally:
		if client:
			await client.close()

def set_config(product_name, ip_address, timeout_seconds, parameter):
	return asyncio.run(_set_config(product_name, ip_address, timeout_seconds, parameter))
