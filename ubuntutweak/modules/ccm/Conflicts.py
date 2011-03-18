# -*- coding: UTF-8 -*-

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors: Quinn Storm (quinn@beryl-project.org)
#          Patrick Niklaus (marex@opencompositing.org)
#          Guillaume Seguin (guillaume@segu.in)
#          Christopher Williams (christopherw@verizon.net)
# Copyright (C) 2007 Quinn Storm

from gi.repository import Gtk

from Constants import *
from Utils import *

import locale
import gettext
locale.setlocale(locale.LC_ALL, "")
gettext.bindtextdomain("ccsm", DataDir + "/locale")
gettext.textdomain("ccsm")
_ = gettext.gettext

class Conflict:
    def __init__(self, autoResolve):
        self.AutoResolve = autoResolve

    # buttons = (text, type/icon, response_id)
    def Ask(self, message, buttons, custom_widgets=None):
        if self.AutoResolve:
            return Gtk.ResponseType.YES

        dialog = Gtk.MessageDialog(flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.WARNING)

        for text, icon, response in buttons:
            button = Gtk.Button(text)
            button.set_image(Gtk.Image.new_from_stock(icon, Gtk.IconSize.BUTTON))
            dialog.add_action_widget(button, response)

        if custom_widgets != None:
            for widget in custom_widgets:
                dialog.vbox.pack_start(widget, False, False)

        dialog.set_markup(message)
        dialog.show_all()
        answer = dialog.run()
        dialog.destroy()

        return answer

class ActionConflict (Conflict):

    ActionTypes = set(('Bell', 'Button', 'Edge', 'Key'))

    def __init__ (self, setting, settings, autoResolve):

        def ExcludeInternal (settings):
            for setting in settings:
                if not setting.Info[0]:
                    yield setting

        Conflict.__init__(self, autoResolve)
        self.Conflicts = []
        self.Name = ""
        self.Setting = setting

        if settings is None:
            settings = []

        self.Settings = settings

        # if the action is internal, include all global actions plus internal
        # actions from the same plugin. If it is global, include all actions.

        if not settings:
            for n in self.Setting.Plugin.Context.Plugins:
                plugin = self.Setting.Plugin.Context.Plugins[n]
                if plugin.Enabled:
                    pluginActions = GetSettings(plugin, types=self.ActionTypes)

                    if len(setting.Info) and setting.Info[0] and plugin is not setting.Plugin:
                        settings.extend(ExcludeInternal(pluginActions))
                    else:
                        settings.extend(pluginActions)

    def Resolve (self, updater = None):
        if len (self.Conflicts):
            for setting in self.Conflicts:
                answer = self.AskUser (self.Setting, setting)
                if answer == Gtk.ResponseType.YES:
                    setting.Value = 'Disabled'
                    if updater:
                        updater.UpdateSetting (setting)
                if answer == Gtk.ResponseType.NO:
                    return False

        return True

    def AskUser (self, setting, conflict):
        msg = _("The new value for the %(binding)s binding for the action <b>%(action)s</b> "\
              "in plugin <b>%(plugin)s</b> conflicts with the action <b>%(action_conflict)s</b> of the <b>%(plugin_conflict)s</b> plugin.\n"\
              "Do you wish to disable <b>%(action_conflict)s</b> in the <b>%(plugin_conflict)s</b> plugin?")

        msg_dict = {'binding': self.Name,
                    'action': setting.ShortDesc,
                    'plugin': setting.Plugin.ShortDesc,
                    'action_conflict': conflict.ShortDesc,
                    'plugin_conflict': conflict.Plugin.ShortDesc}

        msg = msg % protect_markup_dict (msg_dict)

        yesButton    = (_("Disable %(action_conflict)s") % msg_dict,  Gtk.STOCK_YES,  Gtk.ResponseType.YES)
        noButton     = (_("Don't set %(action)s") %  msg_dict,    Gtk.STOCK_NO,   Gtk.ResponseType.NO)
        ignoreButton = (_("Set %(action)s anyway") % msg_dict,    Gtk.STOCK_STOP, Gtk.ResponseType.REJECT)

        return self.Ask (msg, (ignoreButton, noButton, yesButton))

class KeyConflict(ActionConflict):
    def __init__(self, setting, newValue, settings=None, autoResolve=False, ignoreOld=False):
        ActionConflict.__init__(self, setting, settings, autoResolve)
        self.Name = _("key")

        if not newValue:
            return

        newValue = newValue.lower ()
        oldValue = self.Setting.Value.lower ()
        badValues = ["disabled", "none"]
        if not ignoreOld:
            badValues.append (oldValue)
        if newValue in badValues:
            return

        for s in self.Settings:
            if s is setting:
                continue
            if s.Type == 'Key':
                if s.Value.lower() == newValue:
                    self.Conflicts.append (s)

class ButtonConflict(ActionConflict):
    def __init__(self, setting, newValue, settings=None, autoResolve=False, ignoreOld=False):
        ActionConflict.__init__(self, setting, settings, autoResolve)
        self.Name = _("button")

        if not newValue:
            return

        newValue = newValue.lower ()
        oldValue = self.Setting.Value.lower ()
        badValues = ["disabled", "none"]
        if not ignoreOld:
            badValues.append (oldValue)
        if newValue in badValues:
            return

        for s in self.Settings:
            if s is setting:
                continue
            if s.Type == 'Button':
                if s.Value.lower() == newValue:
                    self.Conflicts.append (s)

class EdgeConflict(ActionConflict):
    def __init__(self, setting, newValue, settings=None, autoResolve=False, ignoreOld=False):
        ActionConflict.__init__(self, setting, settings, autoResolve)
        self.Name = _("edge")

        if not newValue:
            return

        newEdges = set(newValue.split("|"))

        if not ignoreOld:
            oldEdges = set(self.Setting.Value.split("|"))
            diff = newEdges - oldEdges
            if diff:
               newEdges = diff # no need to check edges that were already set
            else:
                return

        for s in self.Settings:
            if s is setting:
                continue
            elif s.Type == 'Edge':
                settingEdges = set(s.Value.split("|"))
                union = newEdges & settingEdges
                if union:
                    for edge in union:
                        self.Conflicts.append ((s, edge))
                        break

    def Resolve (self, updater = None):
        if len (self.Conflicts):
            for setting, edge in self.Conflicts:
                answer = self.AskUser (self.Setting, setting)
                if answer == Gtk.ResponseType.YES:
                    value = setting.Value.split ("|")
                    value.remove (edge)
                    setting.Value = "|".join (value)
                    if updater:
                        updater.UpdateSetting (setting)
                if answer == Gtk.ResponseType.NO:
                    return False

        return True

# Not used for plugin dependencies (which are handled by ccs) but own feature checking e.g. image support
class FeatureRequirement(Conflict):
    def __init__(self, context, feature, autoResolve=False):
        Conflict.__init__(self, autoResolve)
        self.Requirements = []
        self.Context = context
        self.Feature = feature

        self.Found = False
        for plugin in context.Plugins.values():
            if feature in plugin.Features:
                self.Found = True
                if not plugin.Enabled:
                    self.Requirements.append(plugin)
    
    def Resolve(self):
        if len(self.Requirements) == 0 and self.Found:
            return True
        elif not self.Found:
            answer = self.ErrorAskUser()
            if answer == Gtk.ResponseType.YES:
                return True
            else:
                return False
        
        for plugin in self.Requirements:
            answer = self.AskUser(plugin)
            if answer == Gtk.ResponseType.YES:
                plugin.Enabled = True
                self.Context.Write()
                return True

    def ErrorAskUser(self):
        msg = _("You are trying to use the feature <b>%(feature)s</b> which is <b>not</b> provided by any plugin.\n"\
                "Do you wish to use this feature anyway?")

        msg_dict = {'feature': self.Feature}

        msg = msg % protect_markup_dict (msg_dict)

        yesButton = (_("Use %(feature)s") % msg_dict,       Gtk.STOCK_YES, Gtk.ResponseType.YES)
        noButton  = (_("Don't use %(feature)s") % msg_dict, Gtk.STOCK_NO,  Gtk.ResponseType.NO)

        answer = self.Ask(msg, (noButton, yesButton))

        return answer

    def AskUser(self, plugin):
        msg = _("You are trying to use the feature <b>%(feature)s</b> which is provided by <b>%(plugin)s</b>.\n"\
                "This plugin is currently disabled.\n"\
                "Do you wish to enable <b>%(plugin)s</b> so the feature is available?")

        msg_dict = {'feature': self.Feature,
                    'plugin': plugin.ShortDesc}

        msg = msg % protect_markup_dict (msg_dict)

        yesButton = (_("Enable %(plugin)s") % msg_dict,       Gtk.STOCK_YES, Gtk.ResponseType.YES)
        noButton  = (_("Don't enable %(feature)s") % msg_dict, Gtk.STOCK_NO,  Gtk.ResponseType.NO)

        answer = self.Ask(msg, (noButton, yesButton))

        return answer

class PluginConflict(Conflict):
    def __init__(self, plugin, conflicts, autoResolve=False):
        Conflict.__init__(self, autoResolve)
        self.Conflicts = conflicts
        self.Plugin = plugin

    def Resolve(self):
        for conflict in self.Conflicts:
            if conflict[0] == 'ConflictFeature':
                answer = self.AskUser(self.Plugin, conflict)
                if answer == Gtk.ResponseType.YES:
                    disableConflicts = conflict[2][0].DisableConflicts
                    con = PluginConflict(conflict[2][0], disableConflicts,
                                         self.AutoResolve)
                    if con.Resolve():
                        conflict[2][0].Enabled = False
                    else:
                        return False
                else:
                    return False

            elif conflict[0] == 'ConflictPlugin':
                answer = self.AskUser(self.Plugin, conflict)
                if answer == Gtk.ResponseType.YES:
                    disableConflicts = conflict[2][0].DisableConflicts
                    con = PluginConflict(conflict[2][0], disableConflicts,
                                         self.AutoResolve)
                    if con.Resolve():
                        conflict[2][0].Enabled = False
                    else:
                        return False
                else:
                    return False
            
            elif conflict[0] == 'RequiresFeature':
                answer, choice = self.AskUser(self.Plugin, conflict)
                if answer == Gtk.ResponseType.YES:
                    for plg in conflict[2]:
                        if plg.ShortDesc == choice:
                            enableConflicts = plg.EnableConflicts
                            con = PluginConflict(plg, enableConflicts,
                                                 self.AutoResolve)
                            if con.Resolve():
                                plg.Enabled = True
                            else:
                                return False
                            break
                else:
                    return False

            elif conflict[0] == 'RequiresPlugin':
                answer = self.AskUser(self.Plugin, conflict)
                if answer == Gtk.ResponseType.YES:
                    enableConflicts = conflict[2][0].EnableConflicts
                    con = PluginConflict(conflict[2][0], enableConflicts,
                                         self.AutoResolve)
                    if con.Resolve():
                        conflict[2][0].Enabled = True
                    else:
                        return False
                else:
                    return False

            elif conflict[0] == 'FeatureNeeded':
                answer = self.AskUser(self.Plugin, conflict)
                if answer == Gtk.ResponseType.YES:
                    for plg in conflict[2]:
                        disableConflicts = plg.DisableConflicts
                        con = PluginConflict(plg, disableConflicts,
                                             self.AutoResolve)
                        if con.Resolve():
                            plg.Enabled = False
                        else:
                            return False
                else:
                    return False

            elif conflict[0] == 'PluginNeeded':
                answer = self.AskUser(self.Plugin, conflict)
                if answer == Gtk.ResponseType.YES:
                    for plg in conflict[2]:
                        disableConflicts = plg.DisableConflicts
                        con = PluginConflict(plg, disableConflicts,
                                             self.AutoResolve)
                        if con.Resolve():
                            plg.Enabled = False
                        else:
                            return False
                else:
                    return False

        # Only when enabling a plugin
        types = []
        actionConflicts = []
        if not self.Plugin.Enabled and not self.AutoResolve:
            for setting in GetSettings(self.Plugin):
                conflict = None
                if setting.Type == 'Key':
                    conflict = KeyConflict(setting, setting.Value, ignoreOld=True)
                elif setting.Type == 'Button':
                    conflict = ButtonConflict(setting, setting.Value, ignoreOld=True)
                elif setting.Type == 'Edge':
                    conflict = EdgeConflict(setting, setting.Value, ignoreOld=True)

                # Conflicts were found
                if conflict and conflict.Conflicts:
                    name = conflict.Name
                    if name not in types:
                        types.append(name)
                    actionConflicts.append(conflict)

        if actionConflicts:
            answer = self.AskUser(self.Plugin, ('ConflictAction', types))
            if answer == Gtk.ResponseType.YES:
                for conflict in actionConflicts:
                    conflict.Resolve()

        return True

    def AskUser(self, plugin, conflict):
        msg = ""
        okMsg = ""
        cancelMsg = ""
        widgets = []

        # CCSM custom conflict
        if conflict[0] == 'ConflictAction':
            msg = _("Some %(bindings)s bindings of Plugin <b>%(plugin)s</b> " \
					"conflict with other plugins. Do you want to resolve " \
					"these conflicts?")

            types = conflict[1]
            bindings = ", ".join(types[:-1])
            if len(types) > 1:
                bindings = "%s and %s" % (bindings, types[-1])

            msg_dict = {'plugin': plugin.ShortDesc,
                        'bindings': bindings}

            msg = msg % protect_markup_dict (msg_dict)

            okMsg     = _("Resolve conflicts") % msg_dict
            cancelMsg = _("Ignore conflicts") % msg_dict

        elif conflict[0] == 'ConflictFeature':
            msg = _("Plugin <b>%(plugin_conflict)s</b> provides feature " \
					"<b>%(feature)s</b> which is also provided by " \
					"<b>%(plugin)s</b>")
            
            msg_dict = {'plugin_conflict': conflict[2][0].ShortDesc,
                        'feature': conflict[1],
                        'plugin': plugin.ShortDesc}

            msg = msg % protect_markup_dict (msg_dict)

            okMsg     = _("Disable %(plugin_conflict)s") % msg_dict
            cancelMsg = _("Don't enable %(plugin)s") % msg_dict
        
        elif conflict[0] == 'ConflictPlugin':
            msg = _("Plugin <b>%(plugin_conflict)s</b> conflicts with " \
					"<b>%(plugin)s</b>.")
            msg = msg % protect_markup_dict (msg_dict)

            okMsg = _("Disable %(plugin_conflict)s") % msg_dict
            cancelMsg = _("Don't enable %(plugin)s") % msg_dict
        
        elif conflict[0] == 'RequiresFeature':
            pluginList = ', '.join("\"%s\"" % plugin.ShortDesc for plugin in conflict[2])
            msg = _("<b>%(plugin)s</b> requires feature <b>%(feature)s</b> " \
					"which is provided by the following " \
					"plugins:\n%(plugin_list)s")
            
            msg_dict = {'plugin': plugin.ShortDesc,
                        'feature': conflict[1],
                        'plugin_list': pluginList}

            msg = msg % protect_markup_dict (msg_dict)

            cmb = Gtk.ComboBoxText()
            for plugin in conflict[2]:
                cmb.append_text(plugin.ShortDesc)
            cmb.set_active(0)
            widgets.append(cmb)

            okMsg = _("Enable these plugins")
            cancelMsg = _("Don't enable %(plugin)s") % msg_dict
        
        elif conflict[0] == 'RequiresPlugin':
            msg = _("<b>%(plugin)s</b> requires the plugin <b>%(require)s</b>.")

            msg_dict = {'plugin': plugin.ShortDesc,
                        'require': conflict[2][0].ShortDesc}

            msg = msg % protect_markup_dict (msg_dict)

            okMsg = _("Enable %(require)s") % msg_dict
            cancelMsg = _("Don't enable %(plugin)s") % msg_dict
        
        elif conflict[0] == 'FeatureNeeded':
            pluginList = ', '.join("\"%s\"" % plugin.ShortDesc for plugin in conflict[2])
            msg = _("<b>%(plugin)s</b> provides the feature " \
					"<b>%(feature)s</b> which is required by the plugins " \
					"<b>%(plugin_list)s</b>.")
            
            msg_dict = {'plugin': plugin.ShortDesc,
                        'feature': conflict[1],
                        'plugin_list': pluginList}
            
            msg = msg % protect_markup_dict (msg_dict)

            okMsg = _("Disable these plugins")
            cancelMsg = _("Don't disable %(plugin)s") % msg_dict
        
        elif conflict[0] == 'PluginNeeded':
            pluginList = ', '.join("\"%s\"" % plugin.ShortDesc for plugin in conflict[2])
            msg = _("<b>%(plugin)s</b> is required by the plugins " \
					"<b>%(plugin_list)s</b>.")
            
            msg_dict = {'plugin': plugin.ShortDesc,
                        'plugin_list': pluginList}
            
            msg = msg % protect_markup_dict (msg_dict)

            okMsg = _("Disable these plugins")
            cancelMsg = _("Don't disable %(plugin)s") % msg_dict

        okButton     = (okMsg,     Gtk.STOCK_OK,     Gtk.ResponseType.YES)
        cancelButton = (cancelMsg, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        
        answer = self.Ask(msg, (cancelButton, okButton), widgets)
        if conflict[0] == 'RequiresFeature':
            choice = widgets[0].get_active_text()
            return answer, choice
        
        return answer
        e
