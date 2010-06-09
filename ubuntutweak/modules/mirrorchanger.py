#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
#
# Copyright (C) 2010 muzuiget <muzuiget@gmail.com>
# Copyright (C) 2007-2010 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os
import re
import gtk
import Queue
import logging
import gobject
import subprocess
import threading
import aptsources.distro
import aptsources.sourceslist

from ubuntutweak.policykit import proxy
from ubuntutweak.modules  import TweakModule
from ubuntutweak.common.region import CONTINENT_DICT, REGION_TABLE
from ubuntutweak.common.consts import DATA_DIR

STRING_ALL = "All"
STRING_CHECKED = "Checked"
STRING_NOT_CHECKED = "Not checked"
STRING_HOSTNAME = "hostname"
STRING_PROTOCOL = "protocol"
STRING_PING = "ping"

log = logging.getLogger('MirrorChanger')

class MirrorChanger(TweakModule):
    __title__ = _('Mirror Changer')
    __desc__ = _('Select the fastest update mirror.')
    __icon__ = 'software-properties'
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self, 'mirrorchanger.ui')
                
        self.mirror_list = Mirror.get_mirror_list()
        self.region_dict = Mirror.get_region_dict(self.mirror_list)
        self.continent_pixbuf_dict = Region.get_pixbuf_dict(self.region_dict)
        self.filter_mirror = Mirror(None, None, None)
        
        self.region_treestore = gtk.TreeStore(gobject.TYPE_PYOBJECT)        
        self.mirror_liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        self.mirror_modelfilter = self.mirror_liststore.filter_new()
        self.mirror_modelsort = gtk.TreeModelSort(self.mirror_modelfilter)
        
        self.init_region_treestore()
        self.init_mirror_stores()        
        self.setup_check_status_combobox()
        self.setup_region_treeview()
        self.setup_mirror_treeview()

        self.reparent(self.main_vbox)

    def init_region_treestore(self):
        
        def region_treestore_sort_func(model, iter1, iter2, data=None):
            region1 = model.get_value(iter1, 0)
            region2 = model.get_value(iter2, 0)
            # "All" always on top 
            if region1 == STRING_ALL:
                return - 1
            if region2 == STRING_ALL:
                return 1
            return cmp(region1, region2)
        
        # create nodes
        self.region_treestore.append(None, (STRING_ALL,))
        for continent, fullname_list in self.region_dict.items():
            parent_node = self.region_treestore.append(None, (continent,))
            for fullname in fullname_list:
                self.region_treestore.append(parent_node, (fullname,))
                     
        self.region_treestore.set_sort_func(0, region_treestore_sort_func)
        self.region_treestore.set_sort_column_id(0, gtk.SORT_ASCENDING)
             
    def init_mirror_stores(self):
        
        def mirror_modelfilter_visible_func(model, iter, data=None):
            mirror = model.get_value(iter, 0)
            result = True         
            if self.filter_mirror.fullname is None: 
                pass
            elif mirror.fullname != self.filter_mirror.fullname: 
                result = False
            if self.filter_mirror.continent is None: 
                pass
            elif mirror.continent != self.filter_mirror.continent: 
                result = False
            if self.filter_mirror.test is None: 
                pass 
            elif mirror.test != self.filter_mirror.test: 
                result = False   
            if self.filter_mirror.hostname is None: 
                pass
            elif self.filter_mirror.hostname.lower() not in mirror.hostname.lower() and \
                 self.filter_mirror.hostname.lower() not in mirror.protocol.lower(): 
                result = False
            return result
    
        def mirror_modelsort_sort_func0(model, iter1, iter2, data=None):
            mirror1 = model.get_value(iter1, 0)
            mirror2 = model.get_value(iter2, 0)
            return cmp(mirror1.test, mirror2.test)
        
        def mirror_modelsort_sort_func1(model, iter1, iter2, data=None):
            mirror1 = model.get_value(iter1, 0)
            mirror2 = model.get_value(iter2, 0)
            return cmp(mirror1.test, mirror2.test)
        
        def mirror_modelsort_sort_func2(model, iter1, iter2, data=None):
            mirror1 = model.get_value(iter1, 0)
            mirror2 = model.get_value(iter2, 0)
            return cmp(mirror1.protocol, mirror2.protocol)
        
        def mirror_modelsort_sort_func3(model, iter1, iter2, data=None):
            mirror1 = model.get_value(iter1, 0)
            mirror2 = model.get_value(iter2, 0)
            return cmp(mirror1.hostname, mirror2.hostname)
        
        def mirror_modelsort_sort_func4(model, iter1, iter2, data=None):
            mirror1 = model.get_value(iter1, 0)
            mirror2 = model.get_value(iter2, 0)
            if mirror1.ping.endswith("ms") and mirror2.ping.endswith("ms"):
                return cmp(float(mirror1.ping[:-2]), float(mirror2.ping[:-2]))
            else:
                return cmp(mirror1.ping, mirror2.ping)
        
        for mirror in self.mirror_list:
            self.mirror_liststore.append((mirror,))
        
        self.mirror_modelfilter.set_visible_func(mirror_modelfilter_visible_func)
        
        self.mirror_modelsort.set_sort_func(0, mirror_modelsort_sort_func0)
        self.mirror_modelsort.set_sort_func(1, mirror_modelsort_sort_func1)
        self.mirror_modelsort.set_sort_func(2, mirror_modelsort_sort_func2)
        self.mirror_modelsort.set_sort_func(3, mirror_modelsort_sort_func3)
        self.mirror_modelsort.set_sort_func(4, mirror_modelsort_sort_func4) 
        
    def setup_check_status_combobox(self):
        render = gtk.CellRendererText()
        self.check_status_combobox.pack_start(render)
        self.check_status_combobox.add_attribute(render, "text", 0)

        self.check_status_liststore.append((STRING_ALL,))
        self.check_status_liststore.append((STRING_CHECKED,))
        self.check_status_liststore.append((STRING_NOT_CHECKED,)) 

        self.check_status_combobox.set_active(0)
        
    def setup_region_treeview(self):    
        
        def column_region_cell_data_func0(column, cell, model, iter, data=None):
            region = model.get_value(iter, 0)
            if model.iter_depth(iter) == 0:
                cell.set_property("pixbuf", self.continent_pixbuf_dict[region])
            else:
                cell.set_property("pixbuf", None)
            
        def column_region_cell_data_func1(column, cell, model, iter, data=None):
            region = model.get_value(iter, 0)
            cell.set_property("text", region)
    
        def on_selection_changed(widget, data=None):
            model, iter = widget.get_selected()
            if iter:
                text = model.get_value(iter, 0)
                depth = model.iter_depth(iter)
                if text == STRING_ALL:
                    self.filter_mirror.continent = None
                    self.filter_mirror.fullname = None
                elif depth == 0:
                    self.filter_mirror.continent = text
                    self.filter_mirror.fullname = None
                else:
                    self.filter_mirror.continent = None
                    self.filter_mirror.fullname = text
                self.mirror_modelfilter.refilter()
                
        render = gtk.CellRendererPixbuf()
        column_region = gtk.TreeViewColumn(" ")
        column_region.pack_start(render, False)
        column_region.set_cell_data_func(render, column_region_cell_data_func0)

        render = gtk.CellRendererText()
        column_region.pack_start(render)
        column_region.set_cell_data_func(render, column_region_cell_data_func1)
        column_region.set_sort_column_id(0)
        
        self.region_treeview.append_column(column_region)        
        self.region_treeview.set_headers_visible(False)
        self.region_treeview.set_level_indentation(-20)
        self.region_treeview.set_model(self.region_treestore)
        self.region_treeview.get_selection().connect("changed", on_selection_changed)
        
    def setup_mirror_treeview(self):
        
        def cellrender_toggle_cell_data_func(column, cell, model, iter, data=None):
            mirror = model.get_value(iter, 0)
            cell.set_property("active", mirror.test)
            
        def cellrender_text_cell_data_func0(column, cell, model, iter, data=None):
            path = model.get_path(iter)
            cell.set_property("text", "%02d" % path[0])
            
        def cellrender_text_cell_data_func1(column, cell, model, iter, data=None):
            mirror = model.get_value(iter, 0)
            cell.set_property("text", mirror.protocol)
            
        def cellrender_text_cell_data_func2(column, cell, model, iter, data=None):
            mirror = model.get_value(iter, 0)
            cell.set_property("text", mirror.hostname)
        
        def cellrender_text_cell_data_func3(column, cell, model, iter, data=None):
            mirror = model.get_value(iter, 0)
            cell.set_property("text", mirror.ping)
            
        def on_test_cellrender_toggled(widget, path, data=None):
            path = self.mirror_modelsort.convert_path_to_child_path(path)
            path = self.mirror_modelfilter.convert_path_to_child_path(path)
            mirror = self.mirror_liststore[path][0]
            mirror.test = not mirror.test
            
        render = gtk.CellRendererText()
        column_index = gtk.TreeViewColumn(" ", render)
        column_index.set_cell_data_func(render, cellrender_text_cell_data_func0)
#        column_index.set_sort_column_id(0)
        
        render = gtk.CellRendererToggle()
        render.connect("toggled", on_test_cellrender_toggled)
        column_test = gtk.TreeViewColumn(" ", render)
        column_test.set_cell_data_func(render, cellrender_toggle_cell_data_func)
        column_test.set_sort_column_id(1)
        
        render = gtk.CellRendererText()
        column_protocol = gtk.TreeViewColumn(STRING_PROTOCOL, render)
        column_protocol.set_cell_data_func(render, cellrender_text_cell_data_func1)
        column_protocol.set_sort_column_id(2)       

        render = gtk.CellRendererText()
        column_hostname = gtk.TreeViewColumn(STRING_HOSTNAME, render)
        column_hostname.set_cell_data_func(render, cellrender_text_cell_data_func2)
        column_hostname.set_sort_column_id(3)
        column_hostname.set_expand(True)       
        
        render = gtk.CellRendererText()
        column_ping = gtk.TreeViewColumn(STRING_PING, render)
        column_ping.set_cell_data_func(render, cellrender_text_cell_data_func3)
        column_ping.set_sort_column_id(4)
        
        self.mirror_treeview.append_column(column_index)
        self.mirror_treeview.append_column(column_test)
        self.mirror_treeview.append_column(column_protocol)
        self.mirror_treeview.append_column(column_hostname)
        self.mirror_treeview.append_column(column_ping)
        self.mirror_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.mirror_treeview.set_model(self.mirror_modelsort)
        
    def on_mirror_treeview_button_press_event(self, widget, event, data=None):
        if event.button == 3:
            self.treeview_menu.popup(None, None, None, event.button, event.time)
            return True
        return False
   
    def on_check_status_combobox_changed(self, widget, data=None):
        index = widget.get_active()
        model = widget.get_model()
        value = model[index][0]
        if value == STRING_CHECKED:
            self.filter_mirror.test = True
        elif value == STRING_NOT_CHECKED:
            self.filter_mirror.test = False
        else:
            self.filter_mirror.test = None
        self.mirror_modelfilter.refilter()
        
    def on_search_entry_activate(self, widget, data=None):
        text = widget.get_text()
        if text == "":
            self.filter_mirror.hostname = None
        else:
            self.filter_mirror.hostname = text
        self.mirror_modelfilter.refilter()

    def on_search_entry_icon_press(self, widget, position, event, data=None):
        if position == gtk.ENTRY_ICON_SECONDARY:
            widget.set_text("")
        widget.emit("activate")
    
    # mirror treeview content menu callback
    def on_treeview_menu_selection_done(self, widget, data=None):
        self.mirror_treeview.queue_draw()
    
    def on_check_menuitem_activate(self, widget, data=None):
        model, rows = self.mirror_treeview.get_selection().get_selected_rows()
        if len(rows) > 0:
            for path in rows:
                mirror = model[path][0]
                mirror.test = True
                self.mirror_treeview.get_selection().unselect_all()
        
    def on_uncheck_menuitem_activate(self, widget, data=None):
        model, rows = self.mirror_treeview.get_selection().get_selected_rows()
        if len(rows) > 0:
            for path in rows:
                mirror = model[path][0]
                mirror.test = False 
                self.mirror_treeview.get_selection().unselect_all()

    def on_select_all_menuitem_activate(self, widget, data=None):
        self.mirror_treeview.get_selection().select_all()
    
    def on_select_none_menuitem_activate(self, widget, data=None):
        self.mirror_treeview.get_selection().unselect_all()
        
    def on_invert_selection_activate(self, widget, data=None):
        selection = self.mirror_treeview.get_selection()
        rows = selection.get_selected_rows()[1]
        selection.select_all()
        for path in rows:
            selection.unselect_path(path)         
        
    # action buttons
    def on_test_button_clicked(self, widget, data=None):                
        mirror_list = []
        for row in self.mirror_liststore:
            mirror = row[0]
            if mirror.test:
                mirror.ping = Mirror.PING_WAITING
                mirror_list.append(mirror)
        
        if len(mirror_list) > 0:
            widget.set_sensitive(False)
            self.running = threading.Event()
            self.running.set()
            mirrorTest = MirrorTest(mirror_list, self.running, self)
            mirrorTest.start()
        self.stop_button.set_sensitive(True)
        self.mirror_treeview.queue_draw()
    
    def on_stop_button_clicked(self, widget, data=None):
        if (self.running is not None) and self.running.isSet():
            self.running.clear()
        self.test_button.set_sensitive(True)

        for row in self.mirror_liststore:
            mirror = row[0]
            if  mirror.ping == Mirror.PING_WAITING:
                mirror.ping = Mirror.PING_STOPPED
        self.mirror_modelsort.set_sort_column_id(4, gtk.SORT_ASCENDING)
        widget.set_sensitive(False)
        self.mirror_treeview.queue_draw()
        
    def on_change_button_clicked(self, widget, data=None):
        model, rows = self.mirror_treeview.get_selection().get_selected_rows()
        if len(rows) == 1:            
            path = rows[0]
            mirror = model[path][0]
            url = "%s://%s/%s" % (mirror.protocol, mirror.hostname, mirror.dir)
            text = Mirror.get_sources_list_text(url)
            dialog = SourceslistDialog(text)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                result = proxy.edit_file("/etc/apt/sources.list", text)
                if result != 'error':
                    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                               gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                               "Update success!")
                else:
                    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                               gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                               "Update fail!")
                dialog.run()
                dialog.destroy()
        else:
            dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                       "You should select one mirror")
            dialog.run()
            dialog.destroy()

            
class SourceslistDialog():
    
    def __init__(self, text=None):
        
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(DATA_DIR, 'ui', "sourceslist_dialog.ui"))
        builder.connect_signals(self)     

        self.sourceslist_dialog = builder.get_object("sourceslist_dialog")
        self.preview_buffer = builder.get_object("preview_textbuffer")
        
        if not text is None:
            self.set_text(text)
      
    def run(self):
        return self.sourceslist_dialog.run()
        
    def destroy(self):
        self.sourceslist_dialog.destroy()
        
    def set_text(self, text):
        self.preview_buffer.set_text(text)

class Region():
          
    data_list = REGION_TABLE.split("\n")
    region_list = []
    for line in data_list:
        region = line[:13].split()
        region.append(line[14:])
        region_list.append(region)
    
    @staticmethod
    def get_fullname_by_code(code):
        key = Region.get_region_by_code(code)[4]
        index = key.find(",")
        if index != -1:
            return key[:index]
        else:
            return key
        
    @staticmethod
    def get_continent_by_code(code):
        key = Region.get_region_by_code(code)[0]
        return CONTINENT_DICT[key]

    @staticmethod
    def get_region_by_code(code):
        for line in Region.region_list:
            if code in  line:
                return line
        return None
        
    @staticmethod
    def get_pixbuf_dict(region_dict):   
        
        def get_icon_pixbuf(name, missing=False):
            try:
                filename = "%s.png" % name.replace(' ', '-').lower()
                path = os.path.join(DATA_DIR, "pixmaps/continent", filename)
                pixbuf = gtk.gdk.pixbuf_new_from_file(path) #@UndefinedVariable
                if pixbuf.get_width() != 24 or pixbuf.get_height() != 24:
                    # should remove later
                    if pixbuf.get_width() == 24:
                        return pixbuf
                    pixbuf = pixbuf.scale_simple(24, 24, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
                return pixbuf
            except:
                if missing:
                    icon = gtk.icon_theme_get_default()
                    return icon.load_icon(gtk.STOCK_MISSING_IMAGE, 24, 0)
                else:
                    return None
                     
        pixbuf_dict = {"All":get_icon_pixbuf("All")}
        for continent in region_dict.keys():    
            name = continent.replace(" ", "_")    
            pixbuf_dict[continent] = get_icon_pixbuf(name)
        return pixbuf_dict
        
class Mirror():
    
    PING_UNKNOWN = "unknown"
    PING_WAITING = "waiting"
    PING_TESTING = "testing"
    PING_TIMEOUT = "timeout"
    PING_STOPPED = "stopped"
    
    distro = aptsources.distro.get_distro()
    sourceslist = aptsources.sourceslist.SourcesList()
    distro.get_sources(sourceslist)
    
    def __init__(self, hostname, location, info):
        self.hostname = hostname
        self.location = location
        if not location is None:
            self.fullname = Region.get_fullname_by_code(location)
            self.continent = Region.get_continent_by_code(location)
        else:
            self.fullname = None
            self.continent = None
        if not info is None:
            self.protocol = info[0]
            self.dir = info[1]
        else:
            self.protocol = None
            self.dir = None
        self.test = False
        self.ping = Mirror.PING_UNKNOWN
        
    @staticmethod
    def get_mirror_list():
        mirror_set = Mirror.distro.source_template.mirror_set
        mirror_list = []
        for mirror in mirror_set.values():
            print mirror.hostname, mirror.location, mirror.repositories[0].get_info()
            m = Mirror(mirror.hostname, mirror.location, mirror.repositories[0].get_info())
            mirror_list.append(m)
        return mirror_list
    
    @staticmethod
    def get_region_dict(mirror_list):
        # remove continent duplications
        continent_list = [mirror.continent for mirror in mirror_list]
        continent_list = list(set(continent_list))
        
        region_dict = {}
        for continent in continent_list:
            region_dict[continent] = []
        for mirror in mirror_list:
            if not mirror.fullname in region_dict[mirror.continent]:
                region_dict[mirror.continent].append(mirror.fullname)
        
        return  region_dict
    
    @staticmethod
    def get_sources_list_text(url):
        Mirror.distro.change_server(url)
        text_list = []
        for source in Mirror.sourceslist:
            if source.file.endswith("sources.list"):
                text_list.append(source.str())
        return "".join(text_list)
    
class MirrorTest(threading.Thread):
    
    class PingWorker(threading.Thread):
                
        def __init__(self, id, jobs, parent):
            threading.Thread.__init__(self)
            self.id = id
            self.jobs = jobs
            self.parent = parent
            self.match_result = re.compile(r"^rtt .* = [\.\d]+/([\.\d]+)/.*")

        def run(self):
            result = None
            while MirrorTest.completed < MirrorTest.todo and \
                  self.parent.running.isSet():
                try:
                    mirror = self.jobs.get(True, 1)
                    hostname = mirror.hostname
                except:
                    continue
                log.debug("Thread %02d pinging %s..." % (self.id , hostname))
                mirror.ping = "testing"
                cmd = "ping -q -c 2 -W 1 -i 0.5 %s" % hostname
                pipe = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE)
                reponse = pipe.stdout.read()

                for line in reponse.split("\n"):
                    result = re.findall(self.match_result, line)
                    if len(result) > 0:
                        break
                if result:
                    mirror.ping = "%.1fms" % float(result[0])
                else:
                    mirror.ping = Mirror.PING_TIMEOUT
                MirrorTest.completed_lock.acquire()
                MirrorTest.completed += 1
                if MirrorTest.completed % 5 == 0:
                    self.parent.redraw_parent_treeview()
                MirrorTest.completed_lock.release()
            log.debug("Thread %02d stoped" % self.id)

    
    def __init__(self, mirror_list, running, parent):
        threading.Thread.__init__(self)
        self.running = running
        self.mirror_list = mirror_list
        self.thread_list = []
        self.parent = parent
        MirrorTest.completed = 0
        MirrorTest.completed_lock = threading.Lock()
        MirrorTest.todo = len(mirror_list)
        
    def run(self):
        jobs = Queue.Queue()
        for mirror in self.mirror_list:
            jobs.put(mirror)
        if len(self.mirror_list) < 20:
            thread_num = len(self.mirror_list)
        else:
            thread_num = 20
        for id in range(thread_num):
            t = MirrorTest.PingWorker(id, jobs, self)
            self.thread_list.append(t)
            log.debug("Thread %02d starting..." % id)
            t.start()             

        for t in self.thread_list:
            t.join()
        self.parent.stop_button.emit("clicked")
    
    def redraw_parent_treeview(self):
        self.parent.mirror_treeview.queue_draw()
