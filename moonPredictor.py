#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


#installing a package
#!pip3 install <package name> 


# In[24]:


import pandas as pd
import math 
import os
from fpdf import FPDF
import webbrowser


# In[25]:


class MoonCalc:
    def __init__(self,file_path,date,Month,year):
            self.path = file_path
            self.date = date
            self.month = Month
            self.year = year
    def data(self,*args):
        def set_axis(df):
            values = ["year","h","cd","conj",
                      "f","wk","mon","day","set",
                      "Saz","age","Alt","Maz","dz",
                      "Mag","El","mset","lag","best","cat"]
            df.set_axis(values,axis = 'columns',inplace = True)
            return df            
        def illum(a):#converting elongation to illumination
            val = 50*(1-math.cos(math.radians(a)))
            val = round(val, 1)
            return val
        try:
            df = pd.read_fwf(args[0]+'\\'+args[1])
        except:
            print("")
        else: 
            df = set_axis(df)
            dfa = df.drop(['f','Mag','wk'],axis = 1)
            dfs = dfa.loc[:,:'conj']
            dfd = dfa.loc[:,'mon':'cat']
            dfd.fillna(method = 'bfill',inplace = True)
            dfs.fillna(method = 'ffill',inplace = True)
    #         #combining dfs
            dfg = dfs.combine_first(dfd)
            dfg.drop_duplicates(inplace = True)
            dfg.dropna(inplace = True)
    #         pd.set_option("display.max_rows", None,'display.max_columns', None)
            #set correct formats
            liste = ['conj','set','mset','best']
            for x in liste:dfg[x] = dfg[x].replace(' ',':',regex=True)
            listf = ['cd','day','year','lag','Alt','Saz','dz','Maz']
            for x in listf:dfg[x] = (dfg[x].astype(int)).astype(str)
            dfg['mon'] = dfg['mon'].str[:3]
            dfg['h'] = dfg['h'].str[:3]
            dfg['date'] = dfg['day']+dfg['mon']+dfg['year']
            dfg['date'] = pd.to_datetime(dfg['date'],format = '%d%b%Y')
            dfg = dfg.set_index('date')
            #create conjunction time column 
            dfg['conj_time'] = dfg['cd']+dfg['h']+dfg['year']+' '+dfg['conj']
            dfg['conj_time'] = pd.to_datetime(dfg['conj_time'])
            #create station column
            if args:
                dfg['Station'] = args[1].split('.',1)[0]
            else:
                dfg['Station'] = self.loc
            #Illumination calculation in func-->illum using Elongation 
            dfg['El'] = dfg['El'].astype(int)
            dfg['ilum'] =  dfg.apply(lambda row : illum(row['El']), axis = 1)
            return dfg        #load data
    def sort(self,*args):#sorting the columns in desired order
        df = self.data(args[0],args[1])
        dfs = pd.DataFrame(df[['Station','set','lag','Alt','Saz','dz','El','ilum','cat','age','conj_time']])
        sorter = ['Karachi', 'Quetta','Lahore','Islamabad','Peshawar','Jiwani','Gilgit','Multan','Muzaffarabad']
        dfs.Station = dfs.Station.astype("category").cat.set_categories(sorter)
        return dfs        
    def all_files(self):# read all files and returns its df
        directory = self.path
        d = []
        df = pd.DataFrame()
        if os.path.exists(directory) == True:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    d = pd.DataFrame(self.sort(root,filename))
                    df = df.append(d)  
                return df
        else: 
            print("directory does not exist")
            return(df)             
    def calculate(self):#returns df with required values                
        dfs = self.all_files()
        date = self.date
        dfd = pd.DataFrame()
        if dfs.empty == False:
            if dfs.loc[date].empty == False:
                dfs = dfs.loc[date].sort_values(['Station'])
                dfd = dfs.loc[:,:'cat']
                dfd.Station = dfd.Station.astype(str) + "(" + dfd.set.astype(str)+")"
                dfd.drop(columns = "set", inplace = True)
                dfd.rename(columns = {'Station':'STATION(Sunset)','lag':'LAG TIME(Minutes)','Alt':'MOON ALTITUDE(Degrees)', 
                                      'Saz':'SUN_AZIMUTH(Degrees)',
                                      'dz':'DAZ(Degrees)',
                                      'El':'ELONGATION(Degrees)','ilum':'ILLUMINATION(%)',
                                      'cat':'CRITERION'}, inplace = True)
               
                    
                return dfd
        else:
            return dfd
    def jiwani(self):
        date = self.date
        dfs = self.all_files()
        date = self.date
        if dfs.empty == False:
            if dfs.loc[date].empty == False:
                dfs = dfs.loc[date].sort_values(['Station'])
                dfs = dfs.loc[dfs.Station == "Jiwani"]
        return(dfs)# return df with jiwani row only
    def pdf(self):
        Format = "Arial"
        
        data = {'Station':'STATION   (Sunset)','lag':'LAG TIME(Min)','Alt':'MOON ALTITUDE(Deg)', 
                                      'Saz':'SUN_AZIMUTH(Deg)',
                                      'dz':'DAZ(Deg)      ',
                                      'El':'ELONGATION(Deg)','ilum':'ILLUMINATION(%)',
                                      'cat':'CRITERION     '}
        df = pd.DataFrame()
        df = self.calculate()
        if df.empty == True: return print("Nothing Found")
        jiwani = self.jiwani()
        dt = str(jiwani.conj_time.dt.strftime("%Y-%m-%d").values[0])
        tm = str(jiwani.conj_time.dt.strftime("%H:%M:%S").values[0])
        age = jiwani.age.values[0].split(" ")
        pdf = FPDF('L', 'mm','A4')
        pdf.add_page()
        pdf.set_font(Format,'B',16)
        h = 7
        w = 297
        pdf.cell(w, h, txt = "PARAMETERS OF THE NEW MOON "+self.month+ " "+ self.year,ln = 1, align = 'C')
        pdf.cell(w, h, txt = "AT THE TIME OF SUNSET ON "+self.date,ln = 1, align = 'C')
        pdf.cell(w, h, txt = f"(Conjunction on {dt} {tm} PST) ",ln = 1, align = 'C')
        pdf.cell(w, h, txt = f"Moon Age at the time of Sunset on {self.date} (Jiwani): {age[0]} hrs {age[1]} mins",ln = 1, align = 'C')
        pdf.ln() 
        pdf.set_font(Format,'B',12)
        li = []
        for x in data.values():li.append(x)
        width = [40,30,38,33,22,31,33,26,40,40]
        start = 25
        pdf.x = start
        offset = pdf.x + width[0]
        sx = pdf.x
        i = 0
        top = 45
        pdf.y = top
        for head in li:    
            pdf.multi_cell(width[i],7,head,border = 1,align = "C")
            # Reset y coordinate
            pdf.y = top
            # Move to computed offset    
            pdf.x = offset
            i += 1
            offset = offset+ width[i]
        h = pdf.font_size * 2.2
        pdf.y = 59
        pdf.set_font(Format,'',12)
        for index, row in df.iterrows():
            i = 0
            pdf.x = start
            for data in row.values:
                pdf.cell(width[i], h, str(data),border = 1,align='C') # write each data for the row in its cell
                i +=1  
            pdf.ln()      
        lines = ["A  Easily visible",
                         "B  Visible under perfect conditions",
                         "C  May need optical aid to find the crescent Moon",
                        "D  Will need optical aid to find the crescent Moon",
                        "E  Not visible with a telescope",
                        "F  Not visible, below the Danjon limit"]
        pdf.ln()
        pdf.set_font(Format, 'B', 12)
        h = 5
        pdf.cell(297, h, txt ="Visibility Criterion: ",ln = 1, align = 'L')
        pdf.set_font(Format, '', 12)
        for line in lines:pdf.cell(297, h, txt = line,ln = 1, align = 'L') 
        pdf.output('tuto1.pdf','F')
        webbrowser.open_new('tuto1.pdf')        # save pdf
    def csv(self,loc):
        df = set_date()
        df.to_csv(loc+self.date+".csv",index = False)        #save csv


# In[ ]:


path = input("Input data directory wrt code file: ")
date = input("Date: ")
month = input("Islamic Month: ")
year = input("Islamic year: ")
Moon = MoonCalc(path,date,month,year +" AH")
Moon.pdf()

