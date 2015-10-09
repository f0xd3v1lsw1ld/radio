__author__ = 'f0xd3v1lsw1ld'
import pygame
# UI classes ---------------------------------------------------------------

# Small resistive touchscreen is best suited to simple tap interactions.
# Importing a big widget library seemed a bit overkill.  Instead, a couple
# of rudimentary classes are sufficient for the UI elements:

# Icon is a very simple bitmap class, just associates a name and a pygame
# image (PNG loaded from icons directory) for each.
# There isn't a globally-declared fixed list of Icons.  Instead, the list
# is populated at runtime from the contents of the 'icons' directory.


class Icon:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        try:
            self.bitmap = pygame.image.load(self.path + '/' + name + '.png')
        except:
            pass


class Textbox:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        self.text = ""
        self.bg = None

    def setText(self, text):
        self.text = text

    def draw(self, text, size, x_pos, y_pos):
        self.bg = pygame.Surface(size=(self.width, self.height))
        self.bg = self.bg.convert()
        self.bg.fill(self.color)
        self.text = text
        font = pygame.font.Font(None, size)
        text = font.render(self.text, 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = self.bg.get_rect().centerx
        self.bg.blit(text, textpos)

        # blit everything to the screen
        screen = pygame.display.get_surface()
        screen.blit(self.bg, (x_pos, y_pos))
        pygame.display.flip()


# Button is a simple tappable screen region.  Each has:
#  - bounding rect ((X,Y,W,H) in pixels)
#  - optional background color and/or Icon (or None), always centered
#  - optional foreground Icon, always centered
#  - optional single callback function
#  - optional single value passed to callback
# Occasionally Buttons are used as a convenience for positioning Icons
# but the taps are ignored.  Stacking order is important; when Buttons
# overlap, lowest/first Button in list takes precedence when processing
# input, and highest/last Button is drawn atop prior Button(s).  This is
# used, for example, to center an Icon by creating a passive Button the
# width of the full screen, but with other buttons left or right that
# may take input precedence (e.g. the Effect labels & buttons).
# After Icons are loaded at runtime, a pass is made through the global
# buttons[] list to assign the Icon objects (from names) to each Button.


class Button:
    def __init__(self, rect, **kwargs):
        self.rect = rect  # Bounds
        self.color = None  # Background fill color, if any
        self.iconBg = None  # Background Icon (atop color fill)
        self.iconFg = None  # Foreground Icon (atop background)
        self.bg = None  # Background Icon name
        self.fg = None  # Foreground Icon name
        self.callback = None  # Callback function
        self.value = None  # Value passed to callback
        self.iconList = []  # Lookup list for icon name validation
        for key, value in kwargs.items():
            #iteritems():
            if key == 'color':
                self.color = value
            elif key == 'bg':
                self.bg = value
            elif key == 'fg':
                self.fg = value
            elif key == 'cb':
                self.callback = value
            elif key == 'value':
                self.value = value

    def selected(self, pos):
        x1 = self.rect[0]
        y1 = self.rect[1]
        x2 = x1 + self.rect[2] - 1
        y2 = y1 + self.rect[3] - 1
        if ((pos[0] >= x1) and (pos[0] <= x2) and
                (pos[1] >= y1) and (pos[1] <= y2)):
            if self.callback:
                if self.value is None:
                    self.callback()
                else:
                    self.callback(self.value)
            return True
        return False

    def draw(self, screen):
        if self.color:
            screen.fill(self.color, self.rect)
        if self.iconBg:
            screen.blit(self.iconBg.bitmap,
                        (self.rect[0] + (self.rect[2] - self.iconBg.bitmap.get_width()) / 2,
                         self.rect[1] + (self.rect[3] - self.iconBg.bitmap.get_height()) / 2))
        if self.iconFg:
            screen.blit(self.iconFg.bitmap,
                        (self.rect[0] + (self.rect[2] - self.iconFg.bitmap.get_width()) / 2,
                         self.rect[1] + (self.rect[3] - self.iconFg.bitmap.get_height()) / 2))

    def setBg(self, name):
        if name is None:
            self.iconBg = None
        else:
            for i in self.iconList:
                if name == i.name:
                    self.iconBg = i
                    break

    def setIconList(self, llist):
        self.iconList = llist