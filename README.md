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

   * Inkscape (version >= 0.92.2)
   * MiKTeX 2.9

Simply download the installer package from the
[latest release](https://github.com/seebk/LaTeXText/releases) and run it.

__NOTE:__ You need at least Inkscape 0.92.2. Prior versions used a different
build environment on Windows and are not compatible with this extension.

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

![Step-by-step animation](https://media.giphy.com/media/3ov9jG1BQAWY9LAOHu/source.gif)

General instructions:

  * Put all text elements on a separate layer.

  * Run 'Extensions -> Render -> Text with Latex (GTK3)'. It will create a new
  layer with all text elements being rendered by `pdflatex`.

  * Switch visibility of the layers to either see the Latex code or to see the
  rendered result.

  * If you changed your Latex code or added new text elements, simply re-run
  the extension and it will update the render layer.

__NOTE:__ There may be two different entries in the Inkscape extension menu: a standard
Inkscape extension and a 'GTK3' GUI variant. The latter is the recommended one
as it can remember and restore previous settings per document and has a more
comfortable UI. The other extension is only there to be used as a fallback if
GTK3 is not available.

#### Options ####

  * _Preamble File_ -- A Latex preamble file to load and configure additional
    packages. The `\documentclass` and `\begin{document}` should not be included,
    see the `preambles/` subfolder for examples.

  * _Document base font size_ -- The main font size for each text element. This
    will correspond to the font size otherwise defined in the `\documentclass`
    statement of a Latex document. Relative font size changes can be set in the
    text with the standard Latex commands (`\small`, `\tiny`, `\Large`, ...).

  * _Scale factor_ -- An additional scaling applied to each rendered element.

  * _SVG/XML tree max. depth_ -- Some imported graphics may have deeply nested
    text elements we do not want to render. If this option is greater than zero
    text elements above the given depth will be ignored.

  * _Add `\\` at every line break_ -- Automatically replace each line break in a
    text element by a Latex line break (`\\`)

  * _Encapsulate all text with $..$_ -- Put all text in math mode by default.

  * _Show log messages_ -- Show log messages for debugging purpose (if there is
    any Latex error the log will be shown anyway)


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

# License

This software is licensed under the GPLv3 license. A copy of the license can
be found in `LICENSE.txt`
