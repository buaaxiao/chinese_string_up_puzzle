#!/usr/bin/python3
# -*- coding:utf-8 -*-

from xml.dom.minidom import parse


class xConfigHandle(object):
    def __init__(self, filename='./config.xml'):
        self.filename = filename
        self.domTree = parse(filename)
        # 文档根元素
        self.rootNode = self.domTree.documentElement

    def get_value(self, element, tag):
        eleNodes = self.rootNode.getElementsByTagName(element)
        if eleNodes.length == 0:
            return None
        for eleNode in eleNodes:
            tagNode = eleNode.getElementsByTagName(tag)
        return tagNode[0].childNodes[0].data

    def set_value(self, section, option, value):
        data = {option: value}
        self.write_config(section, data)

    def write_config(self, element, attribute):
        if not self.domTree.getElementsByTagName(element):
            self.domTree.createElement(element)

    @staticmethod
    def prettyXml(element, indent, newline, level=0):
        # 判断element是否有子元素
        if element:
            # 如果element的text没有内容
            if element.text == None or element.text.isspace():
                element.text = newline + indent * (level + 1)
            else:
                element.text = newline + indent * \
                    (level + 1) + element.text.strip() + \
                    newline + indent * (level + 1)
        # 此处两行如果把注释去掉，Element的text也会另起一行
        # else:
            # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
        temp = list(element)  # 将elemnt转成list
        for subelement in temp:
            # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
            if temp.index(subelement) < (len(temp) - 1):
                subelement.tail = newline + indent * (level + 1)
            else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
                subelement.tail = newline + indent * level
            # 对子元素进行递归操作
            xConfigHandle.prettyXml(
                subelement, indent, newline, level=level + 1)
