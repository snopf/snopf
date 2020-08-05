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
   
    def _updateFocus(f, *args, **kwargs):
        def wrap(self, *args, **kwargs):
            self.setFocus()
            f(self, *args, **kwargs)
            self.clearFocus()
        return wrap
    
    @_updateFocus
    def addLowercase(self):
        '''Add all possible lowercase keys'''
        for char in pg.KEY_TABLE[:pg.PW_GROUP_BOUND_LOWERCASE]:
            self.insert(char)
    
    @_updateFocus
    def addUppercase(self):
        for char in pg.KEY_TABLE[pg.PW_GROUP_BOUND_LOWERCASE:pg.PW_GROUP_BOUND_UPPERCASE]:
            self.insert(char)
    
    @_updateFocus
    def addNumerical(self):
        for char in pg.KEY_TABLE[pg.PW_GROUP_BOUND_UPPERCASE:pg.PW_GROUP_BOUND_DIGIT]:
            self.insert(char)
    
    @_updateFocus
    def addSpecial(self):
        for char in pg.KEY_TABLE[pg.PW_GROUP_BOUND_DIGIT:]:
            self.insert(char)
    
    @_updateFocus        
    def setKeymap(self, keymap):
        self.clear()
        for key in keymap:
            self.insert(pg.KEY_TABLE[key])
            
    def _getKeymap(self):
        return pg.keys_to_keymap(self.text())
    
    def _setKeymap(self, keymap):
        self.clear()
        for key in keymap:
            self.insert(pg.KEY_TABLE[key])
        
    keymap = Property('QVariantList', _getKeymap, _setKeymap)
    
class AppendixEdit(QLineEdit):
    
    '''
    Line Edit for appendix
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(3)

    def getKeys(self):
        return [pg.KEY_TABLE.index(key) for key in self.text()]
    
    def setKeys(self, appendix):
        self.clear()
        for key in appendix:
            self.insert(pg.KEY_TABLE[key])
        
    keys = Property('QVariantList', getKeys, setKeys)
