# yafg: Yet Another Figure Generator
#
# Copyright (c) 2019-2020 Philipp Trommler
#
# SPDX-License-Identifier: GPL-3.0-or-later
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from xml.etree import ElementTree

class YafgTreeprocessor(Treeprocessor):
    def __init__(
            self,
            md,
            stripTitle,
            figureClass,
            figcaptionClass,
            figureNumbering,
            figureNumberClass,
            figureNumberText):
        self.md = md
        self.stripTitle = stripTitle
        self.figureClass = figureClass
        self.figcaptionClass = figcaptionClass
        self.figureNumbering = figureNumbering
        self.figureNumber = 0
        self.figureNumberClass = figureNumberClass
        self.figureNumberText = figureNumberText

    @staticmethod
    def matchChildren(par):
        a = None
        img = par.find("./img")
        if img is None:
            a = par.find("./a")
            if a is not None:
                img = a.find("./img")
                if img is None:
                    a = None
        return (img, a)

    def buildFigureElement(self, par):
            attrib = par.attrib
            par.clear()
            par.tag = "figure"
            for k, v in attrib.items():
                par.set(k, v)
            if self.figureClass is not "":
                par.set("class", self.figureClass)
            par.set("id", "__yafg-figure-{}".format(self.figureNumber))
            par.text = "\n"
            par.tail = "\n"

    def buildFigcaptionElement(self, par, title):
            figcaption = ElementTree.SubElement(par, "figcaption")
            if self.figcaptionClass is not "":
                figcaption.set("class", self.figcaptionClass)
            if self.figureNumbering:
                figureNumberSpan = ElementTree.SubElement(figcaption, "span")
                figureNumberSpan.text = "{}&nbsp;{}:".format(self.figureNumberText, self.figureNumber)
                figureNumberSpan.tail = " {}".format(title)
                if self.figureNumberClass is not "":
                    figureNumberSpan.set("class", self.figureNumberClass)
            else:
                figcaption.text = title
            figcaption.tail = "\n"

    def run(self, root):
        for par in root.findall("./p"):
            img, a = YafgTreeprocessor.matchChildren(par)
            if img is None:
                continue

            self.figureNumber += 1

            self.buildFigureElement(par)
            if a is not None:
                a.tail = "\n"
                par.append(a)
            else:
                img.tail = "\n"
                par.append(img)
            self.buildFigcaptionElement(par, img.get("title"))

            if self.stripTitle:
                del img.attrib["title"]


class YafgExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
                "stripTitle" : [False, "Strip the title from the <img />."],
                "figureClass" : ["", "CSS class to add to the <figure /> element."],
                "figcaptionClass" : ["", "CSS class to add to the <figcaption /> element."],
                "figureNumbering" : [False, "Show the figure number in front of the image caption."],
                "figureNumberClass" : ["", "CSS class to add to the figure number <span /> element."],
                "figureNumberText" : ["Figure", "The text to show in front of the figure number."],
        }
        super(YafgExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        md.treeprocessors.register(
                YafgTreeprocessor(
                    md,
                    stripTitle=self.getConfig("stripTitle"),
                    figureClass=self.getConfig("figureClass"),
                    figcaptionClass=self.getConfig("figcaptionClass"),
                    figureNumbering=self.getConfig("figureNumbering"),
                    figureNumberClass=self.getConfig("figureNumberClass"),
                    figureNumberText=self.getConfig("figureNumberText"),
                ),
                "yafgtreeprocessor",
                8)

def makeExtension(**kwargs):
    return YafgExtension(**kwargs)
