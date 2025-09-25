from . import *
import json
import pygame
from engine.stopwatch import Stopwatch



class Core:

  DEFAULT_PALETTE = [
    (0x80, 0x80, 0x80), (0x00, 0x3D, 0xA6), (0x00, 0x12, 0xB0), (0x44, 0x00, 0x96),
    (0xA1, 0x00, 0x5E), (0xC7, 0x00, 0x28), (0xBA, 0x06, 0x00), (0x8C, 0x17, 0x00),
    (0x5C, 0x2F, 0x00), (0x10, 0x45, 0x00), (0x05, 0x4A, 0x00), (0x00, 0x47, 0x2E),
    (0x00, 0x41, 0x66), (0x00, 0x00, 0x00), (0x05, 0x05, 0x05), (0x05, 0x05, 0x05),
    (0xC7, 0xC7, 0xC7), (0x00, 0x77, 0xFF), (0x21, 0x55, 0xFF), (0x82, 0x37, 0xFA),
    (0xEB, 0x2F, 0xB5), (0xFF, 0x29, 0x50), (0xFF, 0x22, 0x00), (0xD6, 0x32, 0x00),
    (0xC4, 0x62, 0x00), (0x35, 0x80, 0x00), (0x05, 0x8F, 0x00), (0x00, 0x8A, 0x55),
    (0x00, 0x99, 0xCC), (0x21, 0x21, 0x21), (0x09, 0x09, 0x09), (0x09, 0x09, 0x09),
    (0xFF, 0xFF, 0xFF), (0x0F, 0xD7, 0xFF), (0x69, 0xA2, 0xFF), (0xD4, 0x80, 0xFF),
    (0xFF, 0x45, 0xF3), (0xFF, 0x61, 0x8B), (0xFF, 0x88, 0x33), (0xFF, 0x9C, 0x12),
    (0xFA, 0xBC, 0x20), (0x9F, 0xE3, 0x0E), (0x2B, 0xF0, 0x35), (0x0C, 0xF0, 0xA4),
    (0x05, 0xFB, 0xFF), (0x5E, 0x5E, 0x5E), (0x0D, 0x0D, 0x0D), (0x0D, 0x0D, 0x0D),
    (0xFF, 0xFF, 0xFF), (0xA6, 0xFC, 0xFF), (0xB3, 0xEC, 0xFF), (0xDA, 0xAB, 0xEB),
    (0xFF, 0xA8, 0xF9), (0xFF, 0xAB, 0xB3), (0xFF, 0xD2, 0xB0), (0xFF, 0xEF, 0xA6),
    (0xFF, 0xF7, 0x9C), (0xD7, 0xE8, 0x95), (0xA6, 0xED, 0xAF), (0xA2, 0xF2, 0xDA),
    (0x99, 0xFF, 0xFC), (0xDD, 0xDD, 0xDD), (0x11, 0x11, 0x11), (0x11, 0x11, 0x11)
  ]

  pygame.init()
  pygame.font.init()
  
  FONT = pygame.font.SysFont("Consolas", 20)

  def __init__(self, cart: Cart = None, controllers: Controller = [None, None]):
    
    self.interrupt = lambda: None

    self.stopwatch = Stopwatch()
    self.fps_list = [1 for i in range(64)]
    self.fps_ptr = 0
    self.fps = 1


    with open("config.json") as f:
      self.config = json.load(f)

    if "pallete" in self.config.keys():
      pal = self.config["pallete"]
      if pal is str:
        with open(pal, "rb") as f:
          pal = f.read()
        self.palette = []
        for i in range(0, len(pal), 3):
          self.palette.append((pal[i], pal[i+1], pal[i+2]))
      else:
        self.palette = pal
    else:
      self.palette = Core.DEFAULT_PALETTE

    self.cart = None
    self.controllers = [None, None]
    
    self.frame = Frame(self.palette)
    self.ppu = ppu.PPU(self.frame)
    self.ppu.frame.ppu = self.ppu
    self.bus = Bus(self.ppu)
    self.cpu = cpu.CPU(self.bus)

    if controllers[0] is not None:
      self.attach_controller(controllers[0])
    
    if controllers[1] is not None:
      self.attach_controller(controllers[1], player=1)

    if cart is not None:
      self.attach_cart(cart)

  def run(self):
    self.cpu.reset_and_run(frame_interrupt=self.core_interrupt)
  
  def run_without_reset(self):
    self.cpu.run(frame_interrupt=self.core_interrupt)
    
  def reset(self):
    self.cpu.reset()
    self.ppu.reset()
    self.bus.reset()
    
  def core_interrupt(self):
    self.frame.render(self.ppu, new_frame=True)
    frametime = self.stopwatch.lap()
    self.fps_list[self.fps_ptr] = frametime
    self.fps_ptr = self.fps_ptr + 1 & 63
    self.fps = 64 / sum(self.fps_list)
    sleep_time = 1/60 - frametime
    # self.stopwatch.sleep(sleep_time)
    self.interrupt()
    self.frame.update(self.ppu)
    
  def attach_cart(self, cart: Cart):
    self.cart = cart
    self.bus.attach_cart(cart)

  def detach_cart(self):
    self.cart = None
    self.bus.detach_cart()

  def attach_controller(self, controller, player=0):
    self.controllers[player] = controller
    self.bus.attach_controller(controller, player=player)

  def detach_controller(self, player=0):
    self.controllers[player] = None
    self.bus.detach_controller(player=player)
  



  def input_prompt(self, prompt_text):
    # displays a box with a prompt and returns the input string
    def render_box(text_lines):
      rendered_lines = [Core.FONT.render(line, True, (255, 255, 255)) for line in text_lines]
      width = max(text.get_width() for text in rendered_lines)
      height = sum(text.get_height() for text in rendered_lines)
      box = pygame.Surface((width + 20, height + 20))
      box.fill((0, 0, 0))
      y_offset = 10
      for text in rendered_lines:
        box.blit(text, (10, y_offset))
        y_offset += text.get_height()
      self.frame.window.blit(box, (0, 0))
      pygame.display.flip()
    render_box(prompt_text.split('\n'))
    input_str = ""
    input_active = True
    while input_active:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.cpu.killed = True
          input_active = False
          global keep_running
          keep_running = False
          exit()
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_RETURN:
            input_active = False
          elif event.key == pygame.K_BACKSPACE:
            input_str = input_str[:-1]
          elif event.key == pygame.K_ESCAPE:
            input_active = False
            return None
          else:
            input_str += event.unicode
      # Redraw the input box with the current input string
      render_box((prompt_text + input_str).split('\n'))
    return input_str
  

  def display_message(self, message, duration=2):
    def render_box(text_lines):
      rendered_lines = [Core.FONT.render(line, True, (255, 255, 255)) for line in text_lines]
      width = max(text.get_width() for text in rendered_lines)
      height = sum(text.get_height() for text in rendered_lines)
      box = pygame.Surface((width + 20, height + 20))
      box.fill((0, 0, 0))
      y_offset = 10
      for text in rendered_lines:
        box.blit(text, (10, y_offset))
        y_offset += text.get_height()
      self.frame.window.blit(box, (0, 0))
      pygame.display.flip()
    render_box(message.split('\n'))
    stopwatch = Stopwatch()
    stopwatch.reset()
    while stopwatch.time() < duration:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.cpu.killed = True
          global keep_running
          keep_running = False
          exit()
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            return