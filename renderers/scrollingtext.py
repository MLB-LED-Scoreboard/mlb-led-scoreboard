from rgbmatrix import graphics

class ScrollingText:
	def __init__(self, canvas, x, y, width, font, text_color, background_color, text):
		self.canvas = canvas
		self.text = text
		self.text_color = text_color
		self.bg_color = background_color
		self.font = font
		self.x = x
		self.y = y
		self.width = width

	def render(self, scroll_pos):
		x = scroll_pos
		pos = graphics.DrawText(self.canvas, self.font["font"], x, self.y, self.text_color, self.text)
		h = self.font["size"]["height"]
		for x in range(self.x):
			graphics.DrawLine(self.canvas, x, self.y, x, self.y - h, self.bg_color)
		for x in range(self.x + self.width, self.canvas.width):
			graphics.DrawLine(self.canvas, x, self.y, x, self.y - h, self.bg_color)
		return pos
