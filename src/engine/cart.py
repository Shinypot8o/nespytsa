from . import mappers

class Cart:
	ROM_BANK_SIZE = 16384
	ROM_BANK_SHIFT = 14
	chr_BANK_SIZE = 8192
	chr_BANK_SHIFT = 13
	
	MIRROR_HORIZONTAL = 0
	MIRROR_VERTICAL = 1
	MIRROR_4_SCREEN = 2
	
	
	def __init__(self, path):
		
		self.resourcepath = path
		if self.resourcepath.startswith("http://") or self.resourcepath.startswith("https://"):
			import requests
			response = requests.get(self.resourcepath)
			raw_data = response.content
		else:
			with open(self.resourcepath, "rb") as f:
				raw_data = f.read()

		self.write_enable = False

		self.open_data(raw_data)



	def open_data(self, raw_data):

		self.raw_header = raw_data[:16]

		if not self.raw_header[:4] == b"NES\x1a":
			raise Exception("Not a valid iNES file")
		
		self.rom_bank_count = self.raw_header[4]
		self.rom_size = self.rom_bank_count << Cart.ROM_BANK_SHIFT

		self.chr_bank_count = self.raw_header[5]
		self.chr_size = self.chr_bank_count << Cart.chr_BANK_SHIFT

		control_1 = self.raw_header[6]
		control_2 = self.raw_header[7]

		self.mapperid = control_1 >> 4 | control_2 & 0b11110000

		self.four_screen = 0 != control_1 & 0b00001000
		self.trainer_p	 = 0 != control_1 & 0b00000100 # ignore for now
		self.battery_ram = 0 != control_1 & 0b00000010 # ignore for now
		self.v_mirroring = 0 != control_1 & 0b00000001

		self.screen_mirroring = (
			Cart.MIRROR_4_SCREEN if self.four_screen else
			Cart.MIRROR_VERTICAL if self.v_mirroring else
			Cart.MIRROR_HORIZONTAL
		)

		self.version = control_2 >> 2 & 0b00000011
		if self.version != 0:
			raise Exception("Unsupported version " + str(self.version))
		
		self.trainer_size = self.trainer_p << 9

		self.rom_start = 16 | self.trainer_size
		self.rom_end = self.rom_start + self.rom_size

		self.chr_start = self.rom_end
		self.chr_end = self.chr_start + self.chr_size

		self.rom_banks = []
		self.chr_banks = []

		for i in range(self.rom_bank_count):
			start = self.rom_start + i * Cart.ROM_BANK_SIZE
			end = start + Cart.ROM_BANK_SIZE
			self.rom_banks.append(raw_data[start:end])
		
		for i in range(self.chr_bank_count):
			start = self.chr_start + i * Cart.chr_BANK_SIZE
			end = start + Cart.chr_BANK_SIZE
			self.chr_banks.append(raw_data[start:end])
		
		self.mapper = mappers.mappers.get(self.mapperid, None)
		if self.mapper is None:
			raise Exception("Unsupported mapper " + str(self.mapperid))
		self.mapper = self.mapper(self.rom_banks, self.chr_banks)

		self.read_rom = self.mapper.read_rom
		self.write_rom = self.mapper.write_rom
		self.read_chr = self.mapper.read_chr
		self.write_chr = self.mapper.write_chr
		
		print("rom loaded!")
		print(f"mapper: {self.mapperid}")