import cairo, rsvg, math
#from preferences import preferences 
import os

import gtk
(
    SHOW_ALWAYS,
    SHOW_CHILD,
    SHOW_NONE,
) = range(3)

class Cell:
    def __init__(self, 
                ctr = None,
                title = None, 
                icon = None, 
                type = None,
                rect = None):
        self.ctr = ctr
        self.type = type
        
        self.set_rect(rect)
        self.set_padding()
        self.set_icon(icon)
        self.set_title(title)
        
        self.draw_cell()

    def set_rect(self, rect):
        ( self.x, self.y, self.width, self.height ) = rect
        self.rect = rect
        self.draw_background()
        
    def draw_background(self):
        if self.type == SHOW_CHILD:
            self.ctr.set_source_rgb (0.5, 0.5, 0.5)
            self.ctr.rectangle(self.x, self.y, self.width, self.height)
            self.ctr.fill()

    def set_title(self, title=None ):
        if not title:
            return
        self.title = title
        self.title_text_ratio = 0.3
        
#        self.title_size = (self.title_text_ratio * (self.height-2))
        self.title_size = 14
            
        self.title_y = self.title_size + self.left_padding /2

    def set_icon(self, icon):
        self.tile_info_x = self.height
        self.icon_height = 32
        if not icon:
            return
        self.icon = icon

    def set_padding(self):
        self.left_padding = 5
        self.top_padding = 2
    
    def draw_cell( self ):
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
        
    def draw_title( self ):
        style = 0
        font = None
#        alignment = LEFT
#        color = (0,0,0)
#        properties = ( self.title_size, style, font, alignment, color ) 
        self.draw_text(self.title)
        
    def draw_text( self, text):
        if self.type == SHOW_CHILD:
            self.ctr.set_source_rgb (1, 1, 1)

        self.ctr.set_font_size(14)
#        self.ctr.select_font_face('Sans')
#        self.ctr.select_font_face('WenQuanYi ZenHei')
        self.ctr.select_font_face('AR PL UMing CN')
        self.ctr.move_to(48, 24)
        self.ctr.show_text(text)
        self.ctr.stroke()
