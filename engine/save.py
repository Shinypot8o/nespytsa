class Save():
	def __init__(self, ram=None, vram=None, oam=None):
		if ram is None:
			ram = bytearray(0x10000)
		if vram is None:
			vram = bytearray(2048)
		if oam is None:
			oam = bytearray(0x100)
		self.ram = ram
		self.vram = vram
		self.oam = oam
	
	def save(self, core):
		for addr in range(0x10000):
			self.ram[addr] = core.bus.read_funcs[core.bus.read_func_idx[addr]](addr)
		self.vram = core.ppu.vram
		self.oam = core.ppu.oam_data
	
	def load(self, core):
		for addr in range(0x10000):
			core.bus.write_funcs[core.bus.write_func_idx[addr]](addr, self.ram[addr])
		core.ppu.vram = self.vram
		core.ppu.oam_data = self.oam