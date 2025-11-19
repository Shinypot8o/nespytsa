class NROM():
	def __init__(self, rom_banks, chr_banks):
		self.rom_banks = rom_banks
		self.chr_banks = chr_banks
		self.rom_bank_count = len(rom_banks)
		self.chr_bank_count = len(chr_banks)
		assert 0 <= self.rom_bank_count <= 2
		assert 0 <= self.chr_bank_count <= 1

		# mirrors the one or combines the 2
		self.rom = rom_banks[0] + rom_banks[-1]
		
		if self.chr_bank_count == 1:
			self.chr = chr_banks[0]
		else:
			self.chr = bytes([0 for _ in range(0x2000)])

	def read_rom(self, addr):
		return self.rom[addr - 0x8000]

	def write_rom(self, addr, value):
		pass

	def read_chr(self, addr):
		return self.chr[addr]

	def write_chr(self, addr, value):
		# Mapper 0 can have CHR-RAM, but this implementation assumes CHR-ROM.
		# For CHR-ROM, writes are ignored.
		pass