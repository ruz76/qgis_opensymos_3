#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        vysledek.py
# Purpose:     vypoctena hodnota koncentrace/doby prekroceni v ref. bode
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

class Vysledek:
    
    
    def typ_prum(self, idv, x, y,  c_average):
        self.idv = idv        
        self.x = x
        self.y = y
        self.c_average = c_average
    
    def typ_max(self, idv, x, y, c_max, c_max_total):
        self.idv = idv
        self.x = x
        self.y = y
        self.c_max = c_max
        self.c_max_total = c_max_total
    
    def typ_doba(self,idv,x,y,time):
        self.idv = idv
        self.x = x
        self.y = y
        self.time = time
        
    

def main():
    pass

if __name__ == '__main__':
    main() 
