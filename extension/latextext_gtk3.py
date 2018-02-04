#!/usr/bin/env python

######################
#  Check if we can create a nice GTK3 GUI
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
    GTK3_AVAILABLE = True
except ImportError:
    GTK3_AVAILABLE = False
    print("PyGObject module was not found!")
    raise

######################
#  Check if we are in the inkscape extension folder
try:
    import inkex
except ImportError:
    print("GTK3 variant has to be run as an Inkscape extension!")
    raise

from latextext import RenderLatexEffect, SvgProcessor, set_log_level, log_level_debug


######################
# GTK Dialog
#    Extended GTK3 user interface as a replacement of the simple Inkscape
#    default interface
class Gtk3ParamGui(Gtk.Window):

    def __init__(self, run_callback):
        self.run_callback = run_callback
        Gtk.Window.__init__(self, title="LaTexText (GTK3)")
        gh = Gdk.Geometry()
        gh.max_height = 120
        gh.max_width = 700
        self.set_geometry_hints(None, gh, Gdk.WindowHints.MAX_SIZE)
        self.set_hexpand(True)
        self.set_size_request(400, gh.max_height)
        self.set_keep_above(True)

    def prepare_dialog(self, options):

        self.options = options

        grid = Gtk.Grid()
        grid.set_row_spacing(3)
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_border_width(10)
        self.add(grid)

        row_count = 0
        box0 = Gtk.Box(spacing=6)
        grid.attach(Gtk.Label("Preamble File"), 0, row_count, 1, 1)
        self.entryPreamble = Gtk.Entry()
        self.entryPreamble.set_text(options.preamble)
        self.entryPreamble.set_hexpand(True)
        box0.pack_start(self.entryPreamble, True, True, 0)
        btnSelectPreamble = Gtk.Button(label="...")
        btnSelectPreamble.set_hexpand(False)
        btnSelectPreamble.connect("clicked", self.on_select_preamble)
        box0.pack_start(btnSelectPreamble, False, False, 0)
        grid.attach(box0, 1, row_count, 1, 1)

        row_count += 1
        grid.attach(Gtk.Label("Additional Packages"), 0, row_count, 1, 1)
        self.entryPackages = Gtk.Entry()
        self.entryPackages.set_text(options.packages)
        self.entryPackages.set_hexpand(True)
        grid.attach(self.entryPackages, 1, row_count, 1, 1)

        row_count += 1
        grid.attach(Gtk.Label("Document base font size"), 0, row_count, 1, 1)
        self.entryFontsize = Gtk.SpinButton.new_with_range(1, 32, 1)
        self.entryFontsize.set_value(options.fontsize)
        self.entryFontsize.set_hexpand(False)
        grid.attach(self.entryFontsize, 1, row_count, 1, 1)

        row_count += 1
        self.entryScale = Gtk.SpinButton.new_with_range(0.01, 20.0, 0.05)
        self.entryScale.set_digits(2)
        self.entryScale.set_value(options.scale)
        grid.attach(Gtk.Label("Scale factor"), 0, row_count, 1, 1)
        grid.attach(self.entryScale, 1, row_count, 1, 1)

        row_count += 1
        self.entryDepth = Gtk.SpinButton.new_with_range(0, 100, 1)
        self.entryDepth.set_value(options.depth)
        grid.attach(Gtk.Label("SVG/XML tree max. depth"), 0, row_count, 1, 1)
        grid.attach(self.entryDepth, 1, row_count, 1, 1)

        row_count += 1
        grid.attach(Gtk.Label("Add \\\\ at every line break"), 0, row_count, 1, 1)
        self.btnNewline = Gtk.CheckButton()
        self.btnNewline.set_active(options.newline)
        grid.attach(self.btnNewline, 1, row_count, 1, 1)

        row_count += 1
        grid.attach(Gtk.Label("Encapsulate all text with ($..$)"), 0, row_count, 1, 1)
        self.btnMath = Gtk.CheckButton()
        self.btnMath.set_active(options.math)
        grid.attach(self.btnMath, 1, row_count, 1, 1)

        row_count += 1
        grid.attach(Gtk.Label("Show log messages"), 0, row_count, 1, 1)
        self.btnShowLog = Gtk.CheckButton()
        grid.attach(self.btnShowLog, 1, row_count, 1, 1)

        row_count += 2
        box1 = Gtk.Box(spacing=6)
        grid.attach(box1, 0, row_count, 2, 1)

        btnApply = Gtk.Button(label="Apply")
        btnApply.connect("clicked", self.on_btnApply_clicked)
        box1.pack_end(btnApply, False, False, 0)

        btnClose = Gtk.Button(label="Close")
        btnClose.connect("clicked", self.on_btnClose_clicked)
        box1.pack_end(btnClose, False, False, 0)

        self.show_all()
        self.entryScale.grab_focus()
        btnApply.set_can_default(True)
        btnApply.grab_default()
        btnApply.grab_focus()
        self.set_default(btnApply)

    def on_select_preamble(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a Latex preamble file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_keep_above(True)
        dialog.set_modal(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entryPreamble.set_text(dialog.get_filename())

        dialog.destroy()

    def on_btnClose_clicked(self, widget):
        Gtk.main_quit()

    def on_btnApply_clicked(self, widget):
        # get parameters
        self.options.scale = self.entryScale.get_value()
        self.options.depth = self.entryDepth.get_value()
        self.options.fontsize = self.entryFontsize.get_value()
        self.options.preamble = self.entryPreamble.get_text()
        self.options.packages = self.entryPackages.get_text()
        self.options.math = self.btnMath.get_active()
        self.options.newline = self.btnNewline.get_active()
        if self.btnShowLog.get_active() is True:
            set_log_level(log_level_debug)
        try:
            self.run_callback()
        finally:
            Gtk.main_quit()


# Extend standard inkscape extension with the GTK3 GUI
class RenderLatexEffectGTK3(RenderLatexEffect):

    def effect(self):
        svgprocessor = SvgProcessor(self.document, self.options)

        ParamGui = Gtk3ParamGui(svgprocessor.run)
        ParamGui.connect("delete-event", Gtk.main_quit)
        ParamGui.prepare_dialog(svgprocessor.options)
        Gtk.main()


if __name__ == "__main__":
    effect = RenderLatexEffectGTK3()
    effect.affect()
