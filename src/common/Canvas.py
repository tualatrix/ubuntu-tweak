# this file is modified from wine-doors ctile.py
import os
import cairo
import pango
import pangocairo
from Settings import StringSetting

(
    SHOW_ALWAYS,
    SHOW_CHILD,
    SHOW_NONE,
) = range(3)

class RenderCell:
    font_name = StringSetting('/desktop/gnome/interface/font_name').get_string()
    font_size = int(font_name.split()[-1])

    def __init__(self, 
                cell = None,
                ctr = None,
                title = None, 
                icon = None, 
                type = None,
                rect = None):
        self.cell = cell
        self.ctr = ctr
        self.type = type
        
        self.set_rect(rect)
        self.set_padding()
        self.set_icon(icon)
        self.set_title(title)
        
        self.draw_cell()

    def set_rect(self, rect):
        (self.x, self.y, self.width, self.height) = rect
        self.rect = rect
        self.draw_background()
        
    def draw_background(self):
        if self.type == SHOW_CHILD:
            #TODO: the color need to follow the system style
            self.ctr.set_source_rgb (0.5, 0.5, 0.5)
            self.ctr.rectangle(self.x, self.y, self.width, self.height)
            self.ctr.fill()

    def set_title(self, title=None ):
        if not title:
            return
        self.title = title

        self.title_x = self.left_padding * 2 + self.icon_width
        self.title_y = self.icon_height / 2 - self.font_size / 2

    def set_icon(self, icon):
        self.icon_height = 32
        self.icon_width = 32
        if not icon:
            return
        self.icon = icon

    def set_padding(self):
        self.left_padding = 5
        self.top_padding = 2
    
    def draw_cell(self):
        self.ctr.save()
        oy = self.y
        self.ctr.translate( self.x, self.y )

        self.draw_icon()
        self.draw_title()        
    
    def draw_icon( self, x = None, y = None ):
        self.ctr.save()
        if x and y:
            self.ctr.translate( x, y )
        
        self.ctr.translate( self.left_padding, self.top_padding)

        if self.icon.endswith( ".png" ):
            try:
                image = cairo.ImageSurface.create_from_png ( self.icon )
                p_width, p_height = image.get_width(), image.get_height()
                self.icon_width = ( float( self.icon_height )/float( p_height ) ) * float( p_width )
                self.ctr.translate( ( self.icon_height - self.icon_width )/2, 0 )
                if p_width > 1 and p_height > 1 and self.icon_width > 1:
                    self.ctr.scale( self.icon_width/float( p_width ), 
                                   self.icon_width/float( p_height ))
                self.ctr.set_source_surface( image, 0, 0 );
                self.ctr.paint()
            except:
                pass                

        self.ctr.restore()

    def draw_title(self):
        self.draw_text(self.title)
        
    def draw_text(self, text):
        if self.type == SHOW_CHILD:
            self.ctr.set_source_rgb (1, 1, 1)

        self.ctr.move_to(self.title_x, self.title_y)

        layout = self.ctr.create_layout()
        layout.set_text(text)
        layout.set_font_description(pango.FontDescription(self.font_name))

        self.ctr.show_layout(layout)
