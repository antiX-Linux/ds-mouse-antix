#!/usr/bin/env python
#Name: ds-mouse.py
#Depends: python, gtk, xset
#Author: Dave (david@daveserver.info)
#Purpose: Configure mouse on per user basis for a session. This is the gui frontend

import gtk
import os
import re
import gettext
gettext.install("ds-mouse.py", "/usr/share/locale")
class Error:
    def __init__(self, error):
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message_format=_("There is an error,\nplease rerun and correct the following error!")+"\n\n"+error)
        dlg.set_title(_("Successfully updated"))
        dlg.set_keep_above(True) # note: set_transient_for() is ineffective!
        dlg.run()
        dlg.destroy() 
       
class Success:
    def __init__(self, success):
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, message_format=_("Successfully updated")+":\n\n"+success)
        dlg.set_title(_("Successfully updated"))
        dlg.set_keep_above(True) # note: set_transient_for() is ineffective!
        dlg.run()
        dlg.destroy() 
       
class Var: 
    def read(self):        
        var = Var
        var.USER_HOME = os.environ['HOME']
        var.CONF_USER_DIR = var.USER_HOME+"/.desktop-session/"
        var.CONF_USER_FILE = var.CONF_USER_DIR+"mouse.conf"
        var.CONF_SYSTEM_FILE = "/etc/desktop-session/mouse.conf"
        
        if not os.path.exists(var.CONF_USER_DIR):
            os.system("mkdir %s" % (var.CONF_USER_DIR))
            os.system("cp %s %s" % ((var.CONF_SYSTEM_FILE),(var.CONF_USER_DIR)))
        else:
            if not os.path.isfile(var.CONF_USER_FILE):
                os.system("cp %s %s" % ((var.CONF_SYSTEM_FILE),(var.CONF_USER_DIR)))
            
        for line in open(var.CONF_USER_FILE, "r").xreadlines():
            if "#" not in line:
                if re.search(r'^.*=', line):
                    pieces = line.split('=')
                    var.VARIABLE=(pieces[0])
                    var.VARIABLE = re.sub(r'\n', '', var.VARIABLE)
                    OBJECT=(pieces[1])
                    OBJECT = re.sub(r'\n', '', OBJECT)
                    setattr(var, var.VARIABLE, OBJECT)
        
    def write(self, variable, item):
        WRITE_FILE = Var.CONF_USER_FILE+".tmp"
        READ_FILE = Var.CONF_USER_FILE
        
        text = file((WRITE_FILE), "w");text.write("");text.close()
        text = file((WRITE_FILE), "a")
        for line in open(READ_FILE, "r").xreadlines():
            if "#" not in line:
                if re.search(r'^%s=' % (variable), line):
                    text.write (variable+"="+str(item)+"\n") 
                else:
                    text.write (line) 
            else:
                text.write (line) 
        text.close()        
        os.system("mv %s %s" % ((WRITE_FILE), (READ_FILE)))

class mainWindow():
    def apply(self,widget,option):
        if option == 0: #apply button
            acceleration_value = int(self.acceleration.get_value())
            threshold_value = int(self.threshold.get_value())
            size_value = int(self.size.get_value())
            button_order_value = self.order.get_active()
            Var().write('ACCELERATION', acceleration_value)
            Var().write('THRESHOLD', threshold_value)
            Var().write('SIZE', size_value)
            Var().write('BUTTONORDER', button_order_value)
            try:
                os.system("ds-mouse -all")
            except:
                Error(_("Could not run ds-mouse -all"))
            else:
				Success(_("All Options Set"))
        elif option == 1: #reset motion button
            acceleration_value = '-1'
            threshold_value = '-1'
            Var().write('ACCELERATION', acceleration_value)
            Var().write('THRESHOLD', threshold_value)
            try:
                os.system("ds-mouse -a")
            except:
                Error(_("Could not run ds-mouse -a"))
            else:
				Success(_("Mouse Acceleration Reset"))
        elif option == 2: #reset size button
            size_value = '-1'
            Var().write('SIZE', size_value)
            try:
                os.system("ds-mouse -s")
            except:
                Error(_("Could not run ds-mouse -s"))
            else:
				Success(_("Cursor Size Reset"))
        elif option == 3: #change cursor theme button
            try:
                os.system("lxappearance")
            except:
                os.system("rxvt-unicode -tr -sh 65 -fg white -T 'cursor theme' -e su -c 'update-alternatives --config x-cursor-theme' ")
		
    def make_frame(self, text):
        frame = gtk.Frame(_(text))
        frame.set_border_width(10)
        self.mainbox.pack_start(frame)
        frame.show()
        
        self.framebox = gtk.VBox()
        frame.add(self.framebox)
        self.framebox.show()
        
    def make_label(self, text):
        label = gtk.Label()
        label.set_text(_(text))
        self.framebox.pack_start(label)
        label.show()
        
    def scale_set_default_values(self, scale, option):
        scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        scale.set_digits(option)
        scale.set_value_pos(gtk.POS_TOP)
        scale.set_draw_value(True)

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title(_("Mouse Options"))
        window.connect("destroy", lambda w: gtk.main_quit())
        
        self.mainbox = gtk.VBox()
        window.add(self.mainbox)
        self.mainbox.show()
        
        self.make_frame(_("Mouse Acceleration"))
        self.make_label(_("Acceleration (Multiplier)"))
        
        adj1 = gtk.Adjustment(float(Var.ACCELERATION), 0.0, 17.0, 0.1, 1.0, 1.0 )
        self.acceleration = gtk.HScale(adj1)
        self.acceleration.set_size_request(200, 45)
        self.scale_set_default_values(self.acceleration, 1)
        self.framebox.pack_start(self.acceleration)
        self.acceleration.show()
        
        self.make_label(_("Threshold (Pixels)"))
        
        adj1 = gtk.Adjustment(float(Var.THRESHOLD), 0.0, 101.0, 1.0, 1.0, 1.0 )
        self.threshold = gtk.HScale(adj1)
        self.threshold.set_size_request(200, 45)
        self.scale_set_default_values(self.threshold, 1)
        self.framebox.pack_start(self.threshold)
        self.threshold.show()
        
        reset_motion = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        reset_motion.connect("clicked", self.apply, 1)
        self.framebox.pack_start(reset_motion)
        reset_motion.show()
        
        self.make_frame(_("Button Order"))
       
        self.order = gtk.combo_box_new_text()
        self.order.append_text(_("Right hand layout"))
        self.order.append_text(_("Left hand layout"))
        self.order.set_active(int(Var.BUTTONORDER))
        self.framebox.pack_start(self.order)
        self.order.show()
        
        self.make_frame(_("Cursor Size"))
        self.make_label(_("Size (in pixels)"))
        
        adj1 = gtk.Adjustment(float(Var.SIZE), 10.0, 51.0, 1.0, 1.0, 1.0 )
        self.size = gtk.HScale(adj1)
        self.size.set_size_request(200, 45)
        self.scale_set_default_values(self.size, 0)
        self.framebox.pack_start(self.size)
        self.size.show()
        
        reset_size = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        reset_size.connect("clicked", self.apply, 2)
        self.framebox.pack_start(reset_size)
        reset_size.show()
        
        self.make_frame(_("Cursor Theme"))
        self.make_label(_("May require logout/login \nto see the changes.\n"))
        
        theme = gtk.Button(_("Change cursor theme"))
        theme.connect("clicked", self.apply, 3)
        self.framebox.pack_start(theme)
        theme.show()
        
        #BUTTON BOX
        
        buttonbox = gtk.HButtonBox()
        self.mainbox.pack_start(buttonbox)
        buttonbox.show()
        
        aply = gtk.Button(stock=gtk.STOCK_APPLY)
        aply.connect("clicked", self.apply, 0)
        buttonbox.pack_start(aply)
        aply.show()
        
        close = gtk.Button(stock=gtk.STOCK_CLOSE)
        close.connect("clicked", lambda w: gtk.main_quit())
        buttonbox.add(close)
        close.show()
        window.show()

Var().read()
mainWindow()
gtk.main()
