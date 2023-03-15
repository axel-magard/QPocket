# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QListWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QKeySequence
import webbrowser
import sys
import os

file = "ril_export.html"


def getData(file):
    with open(file, encoding="utf-8") as f:
        soup = BeautifulSoup(f,features="lxml")

    links = soup.find_all('a')
    data = []
    tags = set()
    for l in links:
        r = f"<div style='float: left;'><a target='_new_' href='{l['href']}'>{l.getText()}</a></div><div style='float: right;'>"
        for t in l["tags"].split(','):
            tags.add(t)
            r += f"<span style='background-color: #d3d3d3'>{t}</span> "
        r += "</div>"
        data.append([l["href"],l["tags"].split(','),l.getText(),r])

        df = pd.DataFrame(data, columns=['URL', 'Tags','Text','Repr'])
        tagsList = sorted(list(tags))

    return df, tagsList

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Load the ui file
        uic.loadUi("QPocket.ui", self)
        self.searchButton.clicked.connect(self.onSearch)
        self.xButton.clicked.connect(self.onClear)
        self.text1.setFocus()
        self.list2.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list2.clicked.connect(self.onTagSelected)
        self.list1.clicked.connect(self.onItemSelected)


        # Key bindings
        self.onEnter = QShortcut(QKeySequence('Return'), self)
        self.onEnter.activated.connect(self.onSearch)


        # Load data
        self.tagsSelected = []
        self.df, self.tagsList = getData(file)
        # Show data
        self.status.setText("%d record(s)" % self.listRows(self.df,"",self.tagsSelected) )
        self.listTags(self.tagsList)

        # Show the app
        self.show()


    def listRows(self,df,searchText="",tagsSelected=[]):
        self.list1.clear()
        i = 0
        for index, row in self.df.iterrows():
            hit = True
            for s in searchText.split(" "):
                if s.lower() not in row["Text"].lower():
                    hit = False
                else:
                    for t in tagsSelected:
                        if t not in row["Tags"]:
                            hit = False
            if hit:
                item = QListWidgetItem()
                item.setText(row["Text"])
                item.setData(1,row["URL"])
                item = self.list1.insertItem(index,item)
                i += 1
        return i

    def listTags(self,tagsList):
        self.list2.clear()
        for i,t in enumerate(tagsList):
            self.list2.insertItem(i,t)
        return i

    def onClear(self):
        self.text1.setText("")
        self.onSearch()

    def onSearch(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.status.setText("%d record(s)" % self.listRows(self.df,self.text1.text(),self.tagsSelected) )
        QApplication.restoreOverrideCursor()

    def onTagSelected(self):
        sel = self.list2.selectedItems()
        self.tagsSelected = [t.text() for t in sel]
        self.onSearch()

    def onItemSelected(self):
        item = self.list1.currentItem()
        webbrowser.open(item.data(1))


app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()