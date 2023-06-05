#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        main.py
# Purpose:     nastaveni a spusteni vypoctu znecisteni
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

import sys
import time
from .zdroje_bod import ZdrojeBod
from .ref_body import ReferencniBody
from .teren import Teren
from .vypocet import Vypocet
from .vetrna_ruzice import VetrnaRuzice


class Main:
    
    def __init__(self):
        
        self.v = Vypocet()
        self.db_ref_body = ReferencniBody()
        
    
    def inicializuj_zdroje(self, soubor_zdroje):
        self.db_zdroje = ZdrojeBod()
        self.db_zdroje.vytvor_db(soubor_zdroje)
        if len(self.db_zdroje.get_zdroje()) == 0:
            print("Failed to load source file.")
            print("The calculation will be terminated.")

    def inicializuj_zdroje_vrstva(self, layer,id, emission, chimneyHeight, gasVolume, gasTemperature, chimneyDiameter,gasVelocity,usingPerYear,usingPerDay):
        self.db_zdroje = ZdrojeBod()
        self.db_zdroje.vytvor_db_vrstva(layer, id, emission, chimneyHeight, gasVolume, gasTemperature, chimneyDiameter,gasVelocity,usingPerYear,usingPerDay)
        if len(self.db_zdroje.get_zdroje()) == 0:
            print("Failed to load source file.")
            print("The calculation will be terminated.")
            
    def inicializuj_teren(self, soubor_teren):
        self.teren = Teren(soubor_teren)
        
    def inicializuj_vetrnou_ruzici(self, soubor):
        self.vetrna_ruzice = VetrnaRuzice()
        self.vetrna_ruzice.vytvor_ruzici(soubor)
        if len(self.vetrna_ruzice.get_vetrna_ruzice())== 0:
                print("Failed to load wind rose file.")
                print("The calculation will be terminated.")
                
                
    def inicializuj_ref_body(self, layer):
        self.db_ref_body.vytvor_db(layer, self.db_zdroje)
                  
 
    def generuj_sit(self, tl_x, tl_y, lr_x, lr_y, krok):
        self.db_ref_body.generuj_sit(tl_x, tl_y, lr_x, lr_y, krok)
        if len(self.db_ref_body.get_ref_body()) == 0:
            print("The receptor layer is missing.")
            print("The calculation will be terminated.")

        
    def vypocti(self, status, progress, latka, typ_vypocet, imise_limit, vyska_l, vyska_body):
        start_time = time.time()
        status.append(u"Calculation Type: " + str(typ_vypocet))
        status.append(u"Pollutant: " + latka)
        status.append(u"Limit: " + str(imise_limit))
        status.append(u"Receptor height above terrain: " + str(vyska_l))
        if vyska_body == None:
            status.append(u"Terrain elevation: from DEM raster")
        else:        
            status.append(u"Terrain elevation: " + str(vyska_body))
        status.append(u"Calculation in progress, please wait.")
        
        if vyska_body == None:        
            self.db_zdroje.set_z_zdroje(self.teren)
            self.db_ref_body.set_z_refbody(self.teren)
        else:
            self.db_zdroje.set_z_zdroje_custom(vyska_body)
            self.db_ref_body.set_z_refbody_custom(vyska_body)
        
        if typ_vypocet == 1:
            if vyska_body == None:  
                self.v.vypocti_koncentraci(status, progress, 1, latka, self.db_ref_body, 
                                       self.db_zdroje, self.teren, 
                                       None, None, vyska_l, vyska_body)
            else:
                self.v.vypocti_koncentraci(status, progress, 1, latka, self.db_ref_body, 
                                       self.db_zdroje, None, 
                                       None, None, vyska_l, vyska_body)
        elif typ_vypocet == 2:
            if vyska_body == None:  
                self.v.vypocti_koncentraci(status, progress, 2, latka, self.db_ref_body, 
                                       self.db_zdroje, self.teren, 
                                       self.vetrna_ruzice, None, vyska_l, 
                                       vyska_body)
            else:
                self.v.vypocti_koncentraci(status, progress, 2, latka, self.db_ref_body, 
                                       self.db_zdroje, None, 
                                       self.vetrna_ruzice, None, vyska_l, 
                                       vyska_body)      
        elif typ_vypocet == 3:
            if vyska_body == None:  
                self.v.vypocti_koncentraci(status, progress, 3, latka, self.db_ref_body, 
                                       self.db_zdroje, self.teren, 
                                       self.vetrna_ruzice, imise_limit, vyska_l, 
                                       vyska_body)
            else:
                self.v.vypocti_koncentraci(status, progress, 3, latka, self.db_ref_body, 
                                       self.db_zdroje, None, 
                                       self.vetrna_ruzice, imise_limit, vyska_l, 
                                       vyska_body)
            
        end_time = time.time()
        status.append(u"The calculation has been completed. The process lasted " + str(int(end_time - start_time)) + " seconds. The resulting layer was loaded into QGIS.")
    
    
    def export(self, typ_vysledky, typ_export, soubor):
        self.v.export(typ_vysledky, typ_export, soubor)
        
    def get_vysledky(self): 
        return self.v.get_vysledky()
    
    def vypis_vysledky(self,typ_vysledky):
        return self.v.vypis_vysledky(typ_vysledky)
    
    
def main():
    pass

if __name__ == '__main__':
    main()





