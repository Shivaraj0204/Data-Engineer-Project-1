#!/usr/bin/env python
# coding: utf-8

# In[ ]:



import os
import psycopg2
import pandas as pd
import glob
import xlwings as xw
import win32com.client
from PIL import ImageGrab
from datetime import date, datetime, timedelta
import zipfile
from calendar import month_name
import calendar
import warnings
warnings.filterwarnings("ignore")
from xlwings.constants import PasteType
import time
import shutil

# Reading of Input File and getting the entries.

Input_File_Path = 'D:\Python\CENTILITHAILAND\TrueMove_CA_Daily_Report\Driver\TrueMove_Challenge_Arena_Report_Input File.xlsm'

Home_sheet = pd.read_excel(Input_File_Path,sheet_name='Home')
Query_sheet = pd.read_excel(Input_File_Path ,sheet_name='Query')

# # Getting the path from the Input file
directory_path = Home_sheet.iloc[5,2]
Raw_data_path = directory_path + '\\Raw_Data'

# Connecting to NOVA server and getting the Raw_data and Storing in the csv files

import subprocess
x=100

if x == 100:

    for index, row in Query_sheet.iterrows():
        file_name = row['File_Name']
        print(file_name)
        sql_query = row['Query']

        if pd.isna(file_name):
            subprocess.run(["bq", "query", "--use_legacy_sql=false", sql_query], shell=True)
        else:
            query = sql_query
            file_path = Raw_data_path + '\\' + file_name + ".csv"
            subprocess.run([r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe", r"D:\bq2csv\bq2csv.pyc", '--query', query, '--queryOutputFile', file_path], shell=True)

# Open Input file and save so that Formulas will get Updated.

excel_app = xw.App(visible=True)
wb = xw.books.open(Input_File_Path)
wb.save(Input_File_Path)
time.sleep(3)
wb.close()
excel_app.quit()


# Reading of Input File and getting the entries.

Input_File_Path = 'D:\Python\CENTILITHAILAND\TrueMove_CA_Daily_Report\Driver\TrueMove_Challenge_Arena_Report_Input File.xlsm'
Home_sheet = pd.read_excel(Input_File_Path , sheet_name='Home')
Input_sheet = pd.read_excel(Input_File_Path , sheet_name='Input')
Distribute_Mail_sheet = pd.read_excel(Input_File_Path , sheet_name='Distribute_Mail')
External_Mail_sheet = pd.read_excel(Input_File_Path , sheet_name='External_Mail')

directory_path = Home_sheet.iloc[5,2]
Report_name = Home_sheet.iloc[2,2]
Report_save_name = Home_sheet.iloc[3,2]
draft_mail = Home_sheet.iloc[2,5]
Attachment_Type = Home_sheet.iloc[4,2]
remove_formulas_sheet = dict(zip(Input_sheet['Remove_Formulas_Sheet_List'],Input_sheet['Unnamed: 8']))
image_sheet_copy_range = dict(zip(Input_sheet['Sheet_Name'],Input_sheet['Image_Copy_Range']))
Formula_drag_Column_Names = dict(zip(Input_sheet['Formulas_Column'],Input_sheet['Unnamed: 15']))
distribut_To_list = Distribute_Mail_sheet.iloc[2,2]
distribut_CC_list = Distribute_Mail_sheet.iloc[3,2]
external_TO_list = External_Mail_sheet.iloc[2,2]
external_CC_list = External_Mail_sheet.iloc[3,2]
date_check_list = Input_sheet[Input_sheet['Include in Data Check'] == 'YES']['Raw Data File Name'].tolist()

# Getting the path from the Input file

Raw_data_path = directory_path + '\\Raw_Data'
Report_path = directory_path + '\\Driver\\'
Zip_file_Path = directory_path + '\\Report\\'
Backup_Path = directory_path + '\\Driver\\Backup\\'

today_date = date.today()
new_date = today_date - timedelta(days=1)
formated_date = new_date.strftime("%b-%Y")
formated_day = new_date.strftime("%d-%b-%y")


# Check if the Query has run or not.

dir_path = Raw_data_path
files = os.listdir(dir_path)
csv_files = [file for file in files if file.endswith('.csv')]
today = datetime.today()

all_updated = True
for file in csv_files:
    file_path = os.path.join(dir_path, file)
    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
    if file_mtime.date() != today.date():
        all_updated = False
        break

if all_updated != True:
    outlook = win32com.client.Dispatch('outlook.application')
    message = outlook.CreateItem(0)
    message.To = distribut_CC_list
    message.CC = external_CC_list
    message.Subject = Report_save_name + ' || '+  str(formated_date)
    mailBody = '<div style="font-size:15px;">Hi Team,</div>'
    mailBody += '<div>&nbsp;</div>'
    mailBody += f'<div style="font-size:15px;">Report <b>{Report_save_name}</b> is <b style="background-color:orange;">Failed</b> due to SQL Queries are not Run. Please check the tool or contact automation team.'

    mailBody += '<div>&nbsp;</div>'
    mailBody += '<u>Additional Information</u>'
    mailBody += '<div>* Server Info :' + '<a href="url" >\\172.16.21.17\WIN-IP2VHFMS2NT</a>'
    mailBody += '<div>* Path : directory_path</div>'
    mailBody += '<div>* User Name : Administrator</div>'
    mailBody += '<div>* Time Stamp : </div>'
    mailBody += '<div>&nbsp;</div>'
    message.HTMLBody = mailBody
    message.Display()

else:
    # Reading and Storing the Raw data files mentioned in Input file as dictionary

    file_list = os.listdir(Raw_data_path)
    df_list = []
    dict_df = {}
    for file in file_list:
        raw_data_df = pd.read_csv(os.path.join(Raw_data_path, file),index_col = 0)
        df_list.append(raw_data_df)
        file_name = os.path.splitext(file)[0]
        dict_df[file_name] = raw_data_df

    all_have_today_date = True
    dict_row = {}
    for df_name, df in dict_df.items():
        if df_name in date_check_list:
            df.index = pd.to_datetime(df.index)
            dict_row[df_name] = pd.to_datetime((max(df.index.values)))
            if (pd.to_datetime(new_date) != pd.to_datetime((max(df.index.values)))):
                all_have_today_date = False

    if all_have_today_date:
        xl_app = xw.App(visible=True)
        xl_app.calculation='manual'
        Report_wb=xl_app.books.open(Report_path +  Report_name + '.xlsb')

        # Monthly Changes
        if today_date.day == 2:
            for index,row in Input_sheet.iterrows():
                sheet_name = row[17]
                Copy_Range = row[18]
                Paste_Range = row[19]
                sht = Report_wb.sheets[sheet_name]
                data_range = sht.range((Copy_Range))
                target_range = sht.range(Paste_Range)
                data_range.copy()
                target_range.api.PasteSpecial(PasteType.xlPasteValuesAndNumberFormats)
            Report_wb.save(Report_path +   Report_name + '.xlsb')
        # Monthly Changes End

        Raw_Data_sht = Report_wb.sheets['Raw_Data']
        Raw_Data_sht.range("A3:XFD10000").clear_contents()
        for col_name, nan in list(Formula_drag_Column_Names.items())[:-1]:
            Raw_Data_sht.range(col_name + '1:' + col_name + '10000').formula = Raw_Data_sht.range(col_name + '1').formula

        for index, row in Input_sheet.head(5).iterrows():
            paste_range = row['Paste_Range']
            RAW_DATA = dict_df[row['Raw Data File Name']]
            Raw_Data_sht.range(paste_range).value = RAW_DATA

        Report_wb.api.RefreshAll()

        if today_date.day == 1:
            Report_wb.save(Backup_Path + Report_save_name + '- ' + new_date.strftime("%b") + '-' + str(today_date.year) +'.xlsb')

        Report_wb.save(Report_path +   Report_name + '.xlsb')
        for sheet, nan in list(remove_formulas_sheet.items())[:-1]:
            if sheet == 'Summary_123':
                range = Report_wb.sheets[sheet].range('A1:K9')
                range.value = range.value
            else:
                Report_wb.sheets[sheet].used_range.value = Report_wb.sheets[sheet].used_range.value


        remove_sheet = Report_wb.sheets['Raw_Data']
        remove_sheet.delete()
        Report_wb.save(Zip_file_Path + Report_save_name + '.xlsb')
        Report_wb.close()
        xl_app.quit()

        # Image Captureing Part to attach in the Email Body 
        excel_app = xw.App(visible=True)
        workbook_path = Zip_file_Path + Report_save_name + '.xlsb'
        wb = xw.books.open(workbook_path)
        max_attempts = 4
        attempt = 1
        success = False

        while attempt <= max_attempts and not success:
            try:
                for sheet_name, copy_range in list(image_sheet_copy_range.items())[:-1]:
                    sheet = wb.sheets[sheet_name]
                    copyrange = sheet.range(copy_range)
                    time.sleep(4)
                    copyrange.api.CopyPicture(Appearance=1, Format=2)
                    time.sleep(4)
                    ImageGrab.grabclipboard().save(Report_path + sheet_name + '.png')
                success = True
            except Exception as e:
                attempt += 1
                if attempt >= max_attempts:
                    wb.close()
                    excel_app.quit()
                    break
                    
        if success:
            wb.close()
            excel_app.quit()
        else:
            wb.close()
            excel_app.quit()
            sys.exit()

        my_zip = zipfile.ZipFile(Zip_file_Path + Report_save_name + '.zip','w')
        my_zip.write(Zip_file_Path + Report_save_name + '.xlsb', compress_type=zipfile.ZIP_DEFLATED, arcname=Report_save_name + '.xlsb')
        my_zip.close()

        paths = []
        for file in os.listdir(Report_path):
            if file.endswith('.png'):
                paths.append(os.path.abspath(os.path.join(Report_path, file)))

        outlook = win32com.client.Dispatch('outlook.application')
        message = outlook.CreateItem(0)
        message.To = distribut_To_list
        message.CC = distribut_CC_list
        message.Subject = Report_save_name +' || '+  str(formated_date)
        mailBody = '<div >Dear Sir/Madam,</div>'
        mailBody += '<div>&nbsp;</div>'
        mailBody += f'<div>Please find the enclosed <b>{Report_save_name}</b> updated as on ' + f'<font color="Purple"><i>{str(formated_day)}</i></font>' + '.'
        mailBody += "<br><br>"
        for path in paths:
            mailBody += "<img src='" + path + "'><br><br>"
        mailBody += '<div>Regards,</div>'
        mailBody += '<div>GMIS</div>'
        mailBody += '<div style= "color:DodgerBlue;">Empowering Excellence</div>'
        message.HTMLBody = mailBody

        if Attachment_Type == 'Zip':
            zip_attachment_path = Zip_file_Path + Report_save_name + '.zip'
            message.Attachments.Add(Source=zip_attachment_path)
        else:
            excel_attachment_path = Zip_file_Path + Report_save_name + '.xlsb'
            message.Attachments.Add(Source=excel_attachment_path)

        if draft_mail != 0:
            message.Display()
            time.sleep(2)
            message.Send()
        else:
            message.Display()
            time.sleep(2)
            message.Send()
            
        for path in paths:
            os.remove(path)

    else:
        outlook = win32com.client.Dispatch('outlook.application')
        message = outlook.CreateItem(0)
        message.To = external_TO_list
        message.CC = external_CC_list
        message.Subject = '<Failed> : ' +  Report_save_name +' ||'+  str(formated_date)
        mailBody = '<div style="font-size:15px;">Hi Team,</div>'
        mailBody += '<div>&nbsp;</div>'
        mailBody += f'<div style="font-size:15px;">Report <b>{Report_save_name}</b> is <b style="background-color:orange;">Failed</b> due to Data is not updated on ' + f'<font color="Purple"><i>{str(formated_day)}</i></font>' + '.'
        mailBody += '<div>&nbsp;</div>'
        mailBody += '<div style="font-size:15px;">Below is the summary of failure :'

        html = '<html><body><table border="1" cellspacing="2" cellpadding="1" ><tr><th>Table</th><th>Status</th><th>Remark</th></tr>'

        for index, row in Input_sheet.iterrows():
            if row['Include in Data Check'] == 'YES' and dict_row.get(row['Raw Data File Name']) != pd.to_datetime(new_date):
                Table = row['Table']
                Status =  'Failed'
                Remark = 'Last Updated on : ' + str(dict_row.get(row['Raw Data File Name']).strftime("%d-%b-%Y"))
                html += '<tr><td>' + Table + '</td><td style="background-color: #D6EEEE;">' + Status + '</td><td>' + Remark + '</td></tr>'

        html += '</table></body></html>'
        mailBody += html

        mailBody += '<div>&nbsp;</div>'
        mailBody += '<u>Possible Reasons of Failure</u>'
        mailBody += '<div>* File was available on time but data is not loaded in NOVA</div>'
        mailBody += '<div>* File not available in spider</div>'
        mailBody += '<div>* File is corrupt</div>'
        mailBody += '<div>* Connectivity issues</div>'
        mailBody += '<div>&nbsp;</div>'
        mailBody += '<div>OPS/Reporters,</div>'
        mailBody += '<div>Please check at your end and confirm/resolve ASAP.</div>'
        message.HTMLBody = mailBody
        message.Send()
