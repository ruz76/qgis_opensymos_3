#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        db_vysledky.py
# Purpose:     kolekce vysledku, export vysledku do shp a gml
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

import os
from osgeo import ogr
import xml.etree.ElementTree as ET
from xml.dom import minidom

class Vysledky:
    
    def __init__(self):
        self.vysledky = []
        
    def zapis_vysledek(self, vysledek):
        """uklada vypoctene hodnoty koncentraci spolu se souradnicemi 
        ref. bodu jako objekt do listu"""
        self.vysledek = vysledek 
        self.vysledky.append(vysledek)
     
     
    def get_vysledky(self):
        """vrati vsechny vysledky (list objektu Vysledek)"""
        
        return self.vysledky

                
    def vypis_vysledky(self,typ_vysledky):
        
        for v in self.vysledky:
            if typ_vysledky == 1:
                print("Maximalni kratkodoba koncentrace v referencnim bode:")
                print("id: ", getattr(v, "idv"))
                print("x: ",getattr(v, "x"),"y: ",getattr(v, "y"))
                print(("koncentrace: ", getattr(v, "c_max"), getattr(v, "c_max_total")))
            
            elif typ_vysledky == 2:
                print("-------------------------------------------------------")
                print("Prumerna dlouhodoba koncentrace v referencnim bode:")
                print("id: ", getattr(v, "idv"))
                print("x: ",getattr(v, "x"),"y: ",getattr(v, "y"))
                print("koncentrace: ",getattr(v, "c_average"))
            else:
                print("-------------------------------------------------------")
                print("Doba prekroceni koncentraci v referencnim bode:")
                print("id: ",getattr(v, "idv"))
                print("x: ",getattr(v, "x"),"y: ",getattr(v, "y"))
                print("doba prekroceni: ",getattr(v, "time"))
    
               
    def export(self, typ_vysledky, typ_export, soubor):
        "export vysledku do shp nebo gml"
        
        if len(self.vysledky) != 0: 
            if typ_export == "shp":
                driver = ogr.GetDriverByName('Esri Shapefile')
            elif typ_export == "gml":
                driver = ogr.GetDriverByName('GML')
        
            ds = driver.CreateDataSource(soubor)
            layer = ds.CreateLayer('refbody', geom_type=ogr.wkbPoint)
            
            field_id = ogr.FieldDefn('id', ogr.OFTInteger)
            layer.CreateField(field_id)
            
            if typ_vysledky == 1:
                field_tr1_r1 = ogr.FieldDefn('c_cls1_v1', ogr.OFTReal)
                layer.CreateField(field_tr1_r1)
                field_tr2_r1 = ogr.FieldDefn('c_cls2_v1', ogr.OFTReal)
                layer.CreateField(field_tr2_r1)
                field_tr2_r2 = ogr.FieldDefn('c_cls2_v2', ogr.OFTReal)
                layer.CreateField(field_tr2_r2)
                field_tr3_r1 = ogr.FieldDefn('c_cls3_v1', ogr.OFTReal)
                layer.CreateField(field_tr3_r1)
                field_tr3_r2 = ogr.FieldDefn('c_cls3_v2', ogr.OFTReal)
                layer.CreateField(field_tr3_r2)
                field_tr3_r3 = ogr.FieldDefn('c_cls3_v3', ogr.OFTReal)
                layer.CreateField(field_tr3_r3)
                field_tr4_r1 = ogr.FieldDefn('c_cls4_v1', ogr.OFTReal)
                layer.CreateField(field_tr4_r1)
                field_tr4_r2 = ogr.FieldDefn('c_cls4_v2', ogr.OFTReal)
                layer.CreateField(field_tr4_r2)
                field_tr4_r3 = ogr.FieldDefn('c_cls4_v3', ogr.OFTReal)
                layer.CreateField(field_tr4_r3)
                field_tr5_r1 = ogr.FieldDefn('c_cls5_v1', ogr.OFTReal)
                layer.CreateField(field_tr5_r1)
                field_tr5_r2 = ogr.FieldDefn('c_cls5_v2', ogr.OFTReal)
                layer.CreateField(field_tr5_r2)
                field_c_max = ogr.FieldDefn('c_max', ogr.OFTReal)
                layer.CreateField(field_c_max)
            
            elif typ_vysledky == 2:
                field_koncentrace = ogr.FieldDefn('c_average', ogr.OFTReal)
                layer.CreateField(field_koncentrace)
                
            elif typ_vysledky == 3:
                field_time = ogr.FieldDefn('time', ogr.OFTReal)
                layer.CreateField(field_time)
            
            for v in self.vysledky:
                
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(getattr(v, "x"), getattr(v, "y"))
                featureDefn = layer.GetLayerDefn()
                feature = ogr.Feature(featureDefn)
                feature.SetGeometry(point)
                feature.SetField('id', getattr(v, "idv"),)
                if typ_vysledky == 1:
                    c_max = getattr(v, "c_max")
                    c_max_total = getattr(v, "c_max_total")
                    feature.SetField('c_tr1_r1', c_max[0][0])
                    feature.SetField('c_tr2_r1', c_max[1][0])
                    feature.SetField('c_tr2_r2', c_max[2][0])
                    feature.SetField('c_tr3_r1', c_max[3][0])
                    feature.SetField('c_tr3_r2', c_max[4][0])
                    feature.SetField('c_tr3_r3', c_max[5][0])
                    feature.SetField('c_tr4_r1', c_max[6][0])
                    feature.SetField('c_tr4_r2', c_max[7][0])
                    feature.SetField('c_tr4_r3', c_max[8][0])
                    feature.SetField('c_tr5_r1', c_max[9][0])
                    feature.SetField('c_tr5_r2', c_max[10][0])
                    feature.SetField('c_max', c_max_total[0])
                elif typ_vysledky== 2:
                    feature.SetField('c_average', getattr(v, "c_average"))
                elif typ_vysledky == 3:
                    feature.SetField('time', getattr(v, "time"))
                layer.CreateFeature(feature)
            feature.Destroy()
            ds.Destroy()
            print("Vysledky byly exportovany do:",os.path.abspath(soubor))
        
        else:
            print("Soubor nelze vytvorit, nejsou vysledky")


def main():
    pass

if __name__ == '__main__':
    main()
            
        
