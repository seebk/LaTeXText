#!/usr/bin/env python
from __future__ import print_function

import sys
import os
import platform
import subprocess
import tempfile
from lxml import etree


MAC = "Mac OS"
WINDOWS = "Windows"
PLATFORM = platform.system()

INKEX_DEBUG = False
STANDALONE = False

######################
# XML namespace definitions

SVG_NS = u"http://www.w3.org/2000/svg"
INKSCAPE_NS = u"http://www.inkscape.org/namespaces/inkscape"
XLINK_NS = u"http://www.w3.org/1999/xlink"
RENDLTX_NS = u"http://NOTSET"

NSS = {
    u'inkscape': INKSCAPE_NS,
    u'svg': SVG_NS,
    u'xlink': XLINK_NS,
    u'rendltx': RENDLTX_NS,
}

def logln(*msg):
    global QUIET
    global STANDALONE
    if STANDALONE is True:
        print(*msg)
    elif INKEX_DEBUG is True:
        for m in msg:
            inkex.debug(m)

######################
#  Check if we are in the inkscape extension folder
try:
    import inkex
    inkex.localize()
    STANDALONE = False
    QUIET = True
except ImportError:
    STANDALONE = True


######################
# SVG parser
#    Retrieve all text elements, render them with Latex and add the result in
#    a new layer
class SvgParser:

    def __init__(self, infile, options):
        self.options = options
        self.svg_input = infile

        # load from file or use existing document root
        if isinstance(infile, str):
            tree = etree.parse(self.svg_input)
            self.docroot = tree.getroot()
        else:
            self.docroot = infile.getroot()

    def add_id_prefix(self, node, prefix):
        for el in node.xpath('//*[attribute::id]'):
            el.attrib['id'] = prefix + "-" + el.attrib['id']
        for el in node.xpath('//*[attribute::xlink:href]', namespaces=NSS):
            old_href = el.attrib['{%s}href' % XLINK_NS]
            el.attrib['{%s}href' % XLINK_NS] = "#" + prefix + "-" + old_href[1:]
        node.attrib['id'] = prefix

    def insert_node(self, node, root):
        # check if node already exists
        old_node = None
        for el in root.getiterator():
            if 'id' in el.attrib and el.attrib['id'] == node.attrib['id']:
                old_node = el
                root.remove(el)

        # transfer style and transforms etc.
        if old_node is not None:
            if 'transform' in old_node.attrib:
                node.attrib['transform'] = old_node.attrib['transform']

        root.append(node)

    def apply_style(self, node, txt):
        style_txt = txt.attrib['style']
        # TODO: strip spaces from style string before splitting
        properties = dict([item.split(":") for item in style_txt.split(";") if item])
        style_render = ""

        if 'fill' in properties:
            style_render += "fill:" + properties['fill'] + ';'

        node.attrib['style'] = style_render
        for g in node.findall('.//{%s}g' % SVG_NS):
            g.attrib['style'] = style_render
        # TODO: merge with existing style

        return node

    def align_placement(self, node, txt):
        new_pos = (float(txt.attrib['x']), float(txt.attrib['y']))
        # remove position offset, anchor is top/right most element
        pos_list = list()
        for el in node.getiterator():
            if 'x' in el.attrib and 'y' in el.attrib:
                el_pos = (float(el.attrib['x']), float(el.attrib['y']))
                pos_list.append(el_pos)

        pos_list.sort()
        pos_offset = pos_list[0]

        for el in node.getiterator():
            if 'x' in el.attrib:
                el.attrib['x'] = str(float(el.attrib['x']) - pos_offset[0] + new_pos[0])
            if 'y' in el.attrib:
                el.attrib['y'] = str(float(el.attrib['y']) - pos_offset[1] + new_pos[1])

        if 'transform' in txt.attrib:
            node.attrib['transform'] = txt.attrib['transform']
            # TODO: merge with existing transform attribute

        return node

    def run(self):

        lat2svg = Latex2SvgRenderer()

        # check for render layer or add new one
        render_layer = self.docroot.find("{%s}g[@id='ltx-render-layer']" % SVG_NS)
        if render_layer is None:
            logln("Creating a new render layer...")
            render_layer = etree.Element('g')
            render_layer.attrib['{%s}label' % INKSCAPE_NS] = 'Rendered Latex'
            render_layer.attrib['{%s}groupmode' % INKSCAPE_NS] = 'layer'
            render_layer.attrib['id'] = 'ltx-render-layer'
            self.docroot.append(render_layer)
            lat2svg.load_preamble(self.options.preamble)
            render_layer.attrib['{%s}preamble' % RENDLTX_NS] = self.options.preamble
        else:
            logln("Using a previous render layer...")
            preamble_path = render_layer.attrib['{%s}preamble' % RENDLTX_NS]
            if self.options.preamble is not None:
                lat2svg.load_preamble(self.options.preamble)
            elif preamble_path:
                lat2svg.load_preamble(preamble_path)

        for layer in self.docroot.findall('{%s}g' % SVG_NS):
            for txt in layer.findall('{%s}text' % SVG_NS):
                logln("ID: " + txt.attrib['id'])
                # logln("Pos: ", pos)

                latex_string = ""
                tspans = txt.findall('{%s}tspan' % SVG_NS)
                txt_empty = True
                for ts in tspans:
                    if ts.text:
                        latex_string += ts.text + '\\\\\n'
                        txt_empty = False
                    else:
                        latex_string += '\n'
                if txt_empty:
                    logln("Empty text element, skipping...")
                    continue
                logln(latex_string)
                rendergroup = lat2svg.render(latex_string, self.options.scale)
                rendergroup = self.align_placement(rendergroup, txt)
                rendergroup = self.apply_style(rendergroup, txt)
                self.add_id_prefix(rendergroup, 'lx-' + txt.attrib['id'])
                self.insert_node(rendergroup, render_layer)

                parent_layer = txt.getparent()
                if 'transform' in parent_layer.attrib:
                    render_layer.attrib['transform'] = parent_layer.attrib['transform']
                    # TODO: merge with existing transform attribute

        return self.docroot


######################
#  Main converter class
class Latex2SvgRenderer:

    def __init__(self):
        self.preamble = ""

    def __exec_command(self, cmd, ok_return_value=0):
        """
        Run given command, check return value, and return
        concatenated stdout and stderr.
        :param cmd: Command to execute
        :param ok_return_value: The expected return value after successful completion
        """

        try:
            # hides the command window for cli tools that are run (in Windows)
            info = None
            if PLATFORM == WINDOWS:
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                info.wShowWindow = subprocess.SW_HIDE

            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 startupinfo=info)
            out, err = p.communicate()
        except OSError as err:
            logln("Command %s failed: %s" % (' '.join(cmd), err))
            raise RuntimeError()

        if ok_return_value is not None and p.returncode != ok_return_value:
            logln("Command %s failed (code %d): \n\n %s" % (' '.join(cmd), p.returncode, out + err))
            raise RuntimeError()
        return out + err

    def load_preamble(self, filename):
        if filename:
            logln("Loading preamble from " + filename)
            with open(filename, 'r') as preamble_file:
                self.preamble = preamble_file.read()

    def render(self, latex_code, scale=1):
        """
        Create a SVG file from latex code
        """

        # Options pass to LaTeX-related commands
        latexOpts = ['-interaction=nonstopmode',
                     '-halt-on-error']

        texwrapper = r"""
        \documentclass{article}
        \usepackage[a0paper]{geometry}
        \newlength\tindent
        \setlength{\tindent}{\parindent}
        \setlength{\parindent}{0pt}
        \renewcommand{\indent}{\hspace*{\tindent}}
        %s
        \pagestyle{empty}
        \AtBeginDocument{\pdfliteral { %s 0 0 %s 0 0 cm }}
        \begin{document}
            %s
        \end{document}
        """ % (self.preamble, scale, scale, latex_code)

        # Convert TeX to PDF

        tmp_path = tempfile.mkdtemp()
        texfile_path = os.path.join(tmp_path, 'tmp.tex')
        # Write tex
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        f_tex = open(texfile_path, 'w')
        try:
            f_tex.write(texwrapper)
        finally:
            f_tex.close()

        # Exec pdflatex: tex -> pdf
        if PLATFORM == MAC:
            LATEX_PATH = '/Library/TeX/texbin'
        else:
            LATEX_PATH = ''
            
        cmdlog = ""
        try:
            cmd = [os.path.join(LATEX_PATH, 'pdflatex'), texfile_path] + latexOpts
            cmdlog = self.__exec_command(cmd)
        except RuntimeError as error:
            # TODO: cleanup excpetion handling and excception chains
            logln(cmdlog)
            raise RuntimeError("Your LaTeX code has problems:\n\n{errors}".format(errors=cmdlog))

        if not os.path.exists(os.path.join(tmp_path, 'tmp.pdf')):
            logln("pdflatex didn't produce output ", os.path.join(tmp_path, 'tmp.pdf'))
            # TODO: cleanup excpetion handling and excception chains
            raise RuntimeError()

        # Convert PDF to SVG
        self.__exec_command(['pdf2svg', os.path.join(tmp_path, 'tmp.pdf'), os.path.join(tmp_path, 'tmp.svg'), '1'])

        tree = etree.parse(os.path.join(tmp_path, 'tmp.svg'))
        root = tree.getroot()

        rendergroup = etree.Element('g')
        for e in root.getchildren():
            rendergroup.append(e)

        os.chdir(old_cwd)
        return rendergroup


######################
# Init for standalone or Inkscape extension run mode

def add_options(parser):
    parser.add_option("-o", "--outfile", dest="outfile",
                      help="write to output file", metavar="FILE")
    parser.add_option("-p", "--preamble", dest="preamble", default="",
                      help="latex preamble file", metavar="FILE")
    parser.add_option("-s", "--scale", dest="scale", default="1",
                      help="apply additional scaling")
    parser.add_option("-c", "--clean",
                      action="store_false", dest="cleane", default=False,
                      help="remove all renderings")

if STANDALONE is False:

    # Create an Inkscape extension
    class RenderLatexEffect(inkex.Effect):
        def __init__(self):
            inkex.Effect.__init__(self)
            add_options(self.OptionParser)
            self.OptionParser.add_option("-d", "--debug", type='inkbool',
                      action="store", dest="debug", default=False,
                      help="show log messages in inkscape")

        def effect(self):
            global INKEX_DEBUG
            if self.options.debug is True:
                INKEX_DEBUG = True
            svgparse = SvgParser(self.document, self.options)
            svgparse.run()

    # run the extension
    effect = RenderLatexEffect()
    effect.affect()

else:

    # parse commandline arguments
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] SVGfile")
    add_options(parser)
    (options, args) = parser.parse_args()
    if len(args) < 1:
        print('No input file specified! Call with -h argument for usage instructions.')
        sys.exit(1)

    # setup the SVG processor
    svgparse = SvgParser(args[-1], options)
    result = svgparse.run()

    # write processed XML to a file
    xmlstr = etree.tostring(result, pretty_print=True, xml_declaration=True)
    if options.outfile:
        f = open(options.outfile, 'w')
    else:
        f = open(args[-1], 'w')
    f.write(xmlstr.decode('utf-8'))
    f.close()
