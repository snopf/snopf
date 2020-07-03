#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)


import password_generator as pg
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class KeymapValidator(QValidator):
    
    '''
    Ensures that only keys that are part of the keymap can be typed into
    the text field
    '''
    
    def validate(self, inp, pos):
        if len(set(inp)) == len(inp) and all([i in pg.KEY_TABLE for i in inp]):
            return QValidator.Acceptable
        return QValidator.Invalid

class KeymapLineEdit(QLineEdit):
    
    '''
    A line edit that only accepts a maximum of 64 chars which must all
    be part of the keymap.
    Each character can only be used once.
    '''
    
    # Every time the input has changed we signal the change and send
    # the remaining keys
    keymapChanged = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(pg.KEYMAP_SIZE)
        self.setText(''.join(pg.KEY_TABLE))
        self.setValidator(KeymapValidator())
        self.textChanged.connect(self.keymapEdit)
        
    def keymapEdit(self):
        self.fixInput()
        self.keymapChanged.emit(self.remainingKeys())
        
    def fixInput(self):
        '''Sort keys always in the way they are sorted on Snopf'''
        self.setText(''.join(pg.sort_keys(self.text())))
       
    def remainingKeys(self):
        '''Return all characters that are part of the keymap but are not
        typed into the lineedit'''
        return pg.sort_keys(pg.key_table_set.difference(set(self.text())))
   
    def addLowercase(self):
        '''Add all possible lowercase keys'''
        for char in pg.KEY_TABLE[:pg.PW_GROUP_BOUND_LOWERCASE]:
            self.insert(char)
            
    def addUppercase(self):
        for char in pg.KEY_TABLE[pg.PW_GROUP_BOUND_LOWERCASE:pg.PW_GROUP_BOUND_UPPERCASE]:
            self.insert(char)
    
    def addNumerical(self):
        for char in pg.KEY_TABLE[pg.PW_GROUP_BOUND_UPPERCASE:pg.PW_GROUP_BOUND_DIGIT]:
            self.insert(char)
    
    def addSpecial(self):
        for char in pg.KEY_TABLE[pg.PW_GROUP_BOUND_DIGIT:]:
            self.insert(char)
