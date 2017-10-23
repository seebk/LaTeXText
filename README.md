# Introduction

This Inkscape extension searches all text elements in a document and renders
them with PdfLatex. The rendered text will appear at the same position as the 
original text and may contain Latex commands and math formula. Modifications
of the source text will be considered when the extension is executed again.

As the rendered text is added to a new layer, the original document content
is not touched and you can always wipe out all modifications from this extension 
by simply deleting the created layer. 

# Installation

### Linux

Required packages on Debian-based distributions:

  * inkscape (version >= 0.91)
  * texlive-base (pdflatex, ...)
  * pdf2svg
  * python and python-lxml (Python version < 3.0)
  * python-gi, the PyGObject bindings for the GTK3 GUI variant

Run the `install.sh` script to copy the extension into the Inkscape extension
folder in the current user home directory (`~/.config/inkscape/extensions/`).

### Windows

Required Software:

   * Inkscape (version >= 0.91)
   * MiKTeX 2.9

Simply download the installer package and run it. It will occupy
quite a lot of disk space (~100 MB) as it has to install some missing Python
modules as well as required libraries and tools (pdf2svg, PyGObject, GTK3, ...).

### Mac OS X

Required Software:

   * Inkscape (version >= 0.91)
   * MacTex
   * pdf2svg (e.g. installed from Macports)
   * Python lxml module
   * Python PyGObject module for the GTK3 GUI variant

Instructions:

  1. Open a command terminal and check if you can execute `pdflatex`. If it is not
  found verify if MacTex is up-to-date and properly installed.

  2. Install pdf2svg from [Macports](https://www.macports.org/).

         $ sudo port install pdf2svg

  3. Install the required Python modules.

         $ sudo port install py27-gobject3
         $ sudo port install py27-lxml

  4. Macports does not install the Python modules into the default Apple Python
     environment and the official Inkscape OS X installer will not use Python from
     Macports. So we have to install Inkscape from Macports, too.

         $ sudo port install inkscape

     As this pulls quite a lot of dependencies, the download and compilation may
     take a long time. Take a coffee ;)

  5. Run the `install.sh` script to copy the extension into the Inkscape extension
  folder in the current user home directory (`~/.config/inkscape/extensions/`).

If there is an easier way to install and use the extension on OS X, in particular
in combination with the official Inkscape installer, feel free to send updated
instructions.


# Usage

### Inkscape extension

General instructions:

  * Put all text elements on a separate layer.

  * Run 'Extensions -> Render -> Text with Latex (GTK3)'. It will create a new 
  layer with all text elements being rendered by `pdflatex`.

  * Switch visibility of the layers to either see the Latex code or to see the
  rendered result.

  * If you changed your Latex code or added new text elements, simply re-run
  the extension and it will update the render layer.

See the `demo/demo.svg` file to get a full example.

There will be two different entries in the Inkscape extension menu: a standard 
Inkscape extension and a 'GTK3' GUI variant. The latter is the recommended one 
as it can remember and restore previous settings per document and has a more 
comfortable UI. The other extension is only there to be used as a fallback if 
GTK3 is not available.

### Commandline mode

You can directly run the extension in the commandline outside of Inkscape, too.

    Usage: latextext.py [options] SVGfile(s)

    Options:
    -h, --help            show this help message and exit
    -o FILE, --outfile=FILE
                        write to output file or directory
    -p FILE, --preamble=FILE
                        latex preamble file
    -f FONTSIZE, --fontsize=FONTSIZE
                        latex base font size
    -s SCALE, --scale=SCALE
                        apply additional scaling
    -d DEPTH, --depth=DEPTH
                        maximum search depth for grouped text elements
    -n, --newline         insert  ewline at every line break
    -m, --math            encapsulate all text in math mode
    -c, --clean           remove all renderings
    -v, --verbose      


# Credits

Some of the code is based on the [textext](https://pav.iki.fi/software/textext/)
extension. Unfortunately, it is not maintained anymore which was the reason why
I started to work on this extension.

# Licence

GPLv3