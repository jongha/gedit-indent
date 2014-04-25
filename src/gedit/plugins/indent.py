#!/usr/bin/env python

from gi.repository import GObject, Gtk, Gedit, PeasGtk
import ConfigParser

UI_XML = '''<ui>
<menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="Change Indent" action="ChangeIndentPlugin"/>
      </placeholder>
    </menu>
</menubar>
</ui>'''

class ChangeIndentPlugin(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    __gtype_name__ = 'ChangeIndentPlugin'
    window = GObject.property(type=Gedit.Window)

    # config
    config = ConfigParser.ConfigParser()
    config_file = 'indent.cfg'
    spaces = 2
    tab = False

    def __init__(self):
        GObject.Object.__init__(self)
        self._get_config()

    def _add_ui(self):
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup('ChangeIndentActions')
        self._actions.add_actions([
            (
            'ChangeIndentPlugin',
            Gtk.STOCK_INFO,
            'Change Indent',
            '<control><alt>i',
            'Change indent in current document',
            self.on_change_indent
            ),
        ])
        manager.insert_action_group(self._actions)
        self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        manager.ensure_update()

    def do_activate(self):
        self._add_ui()

    def do_deactivate(self):
        self._remove_ui()

    def do_update_state(self):
        pass

    def do_create_configure_widget(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)

        label = Gtk.Label('Change Indent Configuration (Tab to spaces).')
        box.pack_start(label, False, False, 0)

        section = Gtk.Box(spacing=10)
        label = Gtk.Label('Spaces')
        section.pack_start(label, False, False, 0)

        adjustment = Gtk.Adjustment(self.spaces, 2, 10, 1, 10, 0)
        spinbutton = Gtk.SpinButton()
        spinbutton.set_adjustment(adjustment)
        spinbutton.connect("value-changed", self.on_spaces_value_changed)
        section.pack_start(spinbutton, False, False, 0)

        change_tab = Gtk.CheckButton("Spaces to Tab")
        change_tab.connect("toggled", self.on_change_tab_toggled)
        change_tab.set_active(True if self.tab == 1 else False)
        section.pack_start(change_tab, False, False, 0)

        box.pack_start(section, False, False, 0)
        return box

    def on_spaces_value_changed(self, button):
        self.spaces = int(button.get_value())
        self._save_config()

    def on_change_tab_toggled(self, button):
        self.tab = button.get_active()
        self._save_config()

    def on_change_indent(self, action, data=None):
        self._get_config()

        doc = self.window.get_active_document()
        text = ''

        builded_spaces = ''
        for i in range(self.spaces):
            builded_spaces += ' '

        if doc:
            start, end = doc.get_bounds()
            text = doc.get_text(start, end, False)

            stripped_text = []
            for line in text.split('\n'):
                if self.tab:
                    stripped_text.append(line.replace(builded_spaces, '\t'))
                else:
                    stripped_text.append(line.replace('\t', builded_spaces))

            doc.set_text('\n'.join(stripped_text))

    def _get_config(self):
        self.config.read(self.config_file)
        if self.config.has_option('settings', 'tab'):
            self.tab = self.config.getint('settings', 'tab')

        if self.config.has_option('settings', 'spaces'):
            self.spaces = self.config.getint('settings', 'spaces')

    def _save_config(self):
        f = open(self.config_file, 'w')
        if not self.config.has_section('settings'):
            self.config.add_section('settings')

        self.config.set('settings', 'tab', 1 if self.tab else 0)
        self.config.set('settings', 'spaces', self.spaces)
        self.config.write(f)
        f.close()

    def _remove_ui(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_merge_id)
        manager.remove_action_group(self._actions)
        manager.ensure_update()

