class Mapper0():
	def __init__(self, rom_banks, chr_banks):
		self.rom_banks = rom_banks
		self.chr_banks = chr_banks
		self.rom_bank_count = len(rom_banks)
		self.chr_bank_count = len(chr_banks)
		assert 0 <= self.rom_bank_count <= 2
		assert 0 <= self.chr_bank_count <= 1

	def read_rom(self, addr):
		if self.rom_bank_count == 1: # 16KB ROM
			return self.rom_banks[0][addr & 0x3FFF]
		else: # 32KB ROM
			return self.rom_banks[(addr & 0x4000) >> 14][addr & 0x3FFF]

	def write_rom(self, addr, value):
		pass

	def read_chr(self, addr):
		if self.chr_bank_count == 0:
			return 0
		return self.chr_banks[0][addr]

	def write_chr(self, addr, value):
		# Mapper 0 can have CHR-RAM, but this implementation assumes CHR-ROM.
		# For CHR-ROM, writes are ignored.
		pass
		if 0x0000 <= addr <= 0x1FFF:
			return self.chr_banks[0][addr]
		else:
			return 0

	def write_chr(self, addr, value):
		# Mapper 0 can have CHR-RAM, but this implementation assumes CHR-ROM.
		# For CHR-ROM, writes are ignored.
		pass
		if 0x0000 <= addr <= 0x1FFF:
			return self.chr_banks[0][addr]
		else:
			return 0