from enum import Enum, auto
from optparse import Values
import pandas
import io

""" Enumeration of valid PX meta keywords in recomended order. 
    https://www.scb.se/en/services/statistical-programs-for-px-files/px-file-format/recommended-order/
"""
class Keyword(Enum):

    CHARSET = auto()
    AXIS_VERSION = auto()
    CODEPAGE = auto()
    LANGUAGE = auto()
    LANGUAGES = auto()
    CREATION_DATE = auto()

    MATRIX = auto()
    SUBJECT_CODE = auto()
    SUBJECT_AREA = auto()
    TITLE = auto()
    UNITS = auto()
    STUB = auto()
    HEADING = auto()
    VALUES = auto()
    TIMEVAL = auto()
    CODES = auto()


class PxRecord:

    def __init__(self, keyword: Keyword, value: int | str | list[str], language: str=None, subkey: str | list[str]=None):
        self.keyword = keyword
        self.value = value
        self.language = language
        self.subkey = subkey

    def __str__(self):
        if (isinstance(self.value,list)) and (self.language is None) and (isinstance(self.subkey,str)):
            return self.keyword.name.replace("_","-") + '("' + self.subkey + '")=' + ','.join(f'"{w}"' for w in self.value) + ';'
        elif (isinstance(self.value,list)) and (self.language is None):
            return self.keyword.name.replace("_","-") + '=' + ','.join(f'"{w}"' for w in self.value) + ';'

        elif (isinstance(self.value,str)) and (self.language is None):
            return self.keyword.name.replace("_","-") + '="' + self.value + '";'

        elif (isinstance(self.value,str)) and (isinstance(self.language, str)):
            return self.keyword.name.replace("_","-") + '[' + self.language + ']="' + self.value + '";'


# Option 1: Build a PX file record by record
pxRecords = []
pxRecords.append(PxRecord(Keyword.CHARSET, "ANSI"))
pxRecords.append(PxRecord(Keyword.AXIS_VERSION, "2000"))
pxRecords.append(PxRecord(Keyword.CODEPAGE, "utf-8"))
pxRecords.append(PxRecord(Keyword.LANGUAGE, "no"))
#pxRecords.append(PxRecord(Keyword.LANGUAGES, ["no", "en"]))
pxRecords.append(PxRecord(Keyword.SUBJECT_AREA, "Befolkning"))
#pxRecords.append(PxRecord(Keyword.SUBJECT_AREA, "Population", "en"))
pxRecords.append(PxRecord(Keyword.TITLE, "03024: Eksport av oppalen laks etter varegruppe, statistikkvariabel og uke"))
pxRecords.append(PxRecord(Keyword.UNITS, "tonn"))


# Option 2: Build a PX file starting with a Pandas dataframe
# this is csv2 output from https://data.ssb.no/api/v0/no/table/03024 
csv2 = io.StringIO('''"varegruppe","uke","statistikkvariabel","03024: Eksport av oppalen laks,"
"Fersk oppalen laks","2022U11","Vekt (tonn)",17326
"Fersk oppalen laks","2022U11","Kilopris (kr)",78.28
"Fersk oppalen laks","2022U12","Vekt (tonn)",17129
"Fersk oppalen laks","2022U12","Kilopris (kr)",83.53
"Frosen oppalen laks","2022U11","Vekt (tonn)",252
"Frosen oppalen laks","2022U11","Kilopris (kr)",68.99
"Frosen oppalen laks","2022U12","Vekt (tonn)",397
"Frosen oppalen laks","2022U12","Kilopris (kr)",83.13
''')

# this is csv3 output from https://data.ssb.no/api/v0/no/table/03024 (codes output)
csv3 = io.StringIO('''"VareGrupper2","Tid","ContentsCode","03024"
"01","2022U11","Vekt",17326
"01","2022U11","Kilopris",78.28
"01","2022U12","Vekt",17129
"01","2022U12","Kilopris",83.53
"02","2022U11","Vekt",252
"02","2022U11","Kilopris",68.99
"02","2022U12","Vekt",397
"02","2022U12","Kilopris",83.13
''')


df = pandas.read_csv(csv2)
df = df.pivot_table(index='varegruppe', columns=['statistikkvariabel','uke'])

#print(df)
"""
                    03024: Eksport av oppalen laks,                             
statistikkvariabel                    Kilopris (kr)         Vekt (tonn)         
uke                                         2022U11 2022U12     2022U11  2022U12
varegruppe                                                                      
Fersk oppalen laks                            78.28   83.53     17326.0  17129.0
Frosen oppalen laks                           68.99   83.13       252.0    397.0
"""

#print(df.loc[('Fersk oppalen laks','2022U12','Vekt (tonn)'), :])
#print(df.index.names)
#print(df.columns.names)
#print(df.values)

pxRecords.append(PxRecord(Keyword.STUB, df.index.names))
pxRecords.append(PxRecord(Keyword.HEADING, df.columns.names[1:]))
pxRecords.append(PxRecord(Keyword.VALUES, df.index.values.tolist(), None, df.index.name))

#print(df.columns.get_level_values(2))
#print(df.columns.value_counts())
#print(df.columns.values)
print(df.columns.map())

for col in df.columns.names[1:]:
    pxRecords.append(PxRecord(Keyword.VALUES, df.columns.values, None, col))


# Write the PX file
newPxFile = open("new-laks.px", "w")
for record in pxRecords[:]:
    newPxFile.write(str(record) + "\n")
newPxFile.close()