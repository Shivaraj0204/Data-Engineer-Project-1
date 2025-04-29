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

Input_File_Path = 'D:\CA_Asia\Banglalink\DWH_Report\Driver\DWH_Report_Input File.xlsm'

Home_sheet = pd.read_excel(Input_File_Path,sheet_name='Home')
Query_sheet = pd.read_excel(Input_File_Path ,sheet_name='Query')

# # Getting the path from the Input file
directory_path = Home_sheet.iloc[5,2]
Raw_data_path = directory_path + '\\Raw_Data'

# Connecting to NOVA server and getting the Raw_data and Storing in the csv files
import subprocess
x=100

if x==100:
    for index, row in Query_sheet.iterrows():
        file_name = row['File_Name']
        print(file_name)
        sql_query = row['Query']

        if pd.isna(file_name):
            subprocess.run([r"bq", 'query', sql_query], shell=True)
        else:
            query = sql_query
            file_path = Raw_data_path + '\\' + file_name + ".csv"
            print(file_path)
            subprocess.run([r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe", r"D:\bq2csv\bq2csv.pyc", '--query', query, '--queryOutputFile', file_path], shell=True)


# Set the folder where CSV files are stored
csv_folder = r"D:\CA_Asia\Banglalink\DWH_Report\Raw_Data"

# Loop through all CSV files in the folder
for file in os.listdir(csv_folder):
    if file.endswith(".csv"):  # Process only CSV files
        csv_file_path = os.path.join(csv_folder, file)
        xlsx_file_path = csv_file_path.replace(".csv", ".xlsx")

        try:
            # Read CSV and write as XLSX
            df = pd.read_csv(csv_file_path)
            df.to_excel(xlsx_file_path, index=False)

            os.remove(csv_file_path)

        except Exception as e:
            print(f"❌ Error converting {file}: {e}")
# Reading of Input File and getting the entries.

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
formated_date = new_date.strftime("%Y%m%d")
formated_day = new_date.strftime("%d-%b-%y")

Validation_check = pd.read_excel('D:\CA_Asia\Banglalink\DWH_Report\Raw_Data\Validation_Check.xlsx')
Validation = dict(zip(Validation_check['Table_Name'],Validation_check['max_date']))
all_have_today_date = True
for table_name, date in list(Validation.items()):
    if pd.to_datetime(date) < (pd.to_datetime(new_date)):
        all_have_today_date = False
        
if all_have_today_date == True:
    xl_app = xw.App(visible=True)
    xl_app.calculation='manual'
    Report_wb=xl_app.books.open('D:\CA_Asia\Banglalink\DWH_Report\Raw_Data\DWH_Data.xlsx')
    ws = Report_wb.sheets['Sheet1']
    used_range = ws.used_range
    columns_to_format = ["total_round", "total_time_taken_millisec"]
    last_row_C = ws.cells(ws.api.Rows.Count, 'C').end('up').row
    last_row_D = ws.cells(ws.api.Rows.Count, 'D').end('up').row
    used_range_C = ws.range(f'C2:C{last_row_C}')
    used_range_D = ws.range(f'D2:D{last_row_D}')
    

    for col_idx in range(used_range.columns.count):
        column_range = used_range.columns[col_idx]
        column_range.api.Borders(7).LineStyle = 1  # Top border
        column_range.api.Borders(9).LineStyle = 1  # Bottom border
        column_range.api.Borders(7).LineStyle = 1  # Left border
        column_range.api.Borders(10).LineStyle = 1  # Right border

    for row_idx in range(used_range.rows.count):
        row_range = used_range.rows[row_idx]
        row_range.api.Borders(7).LineStyle = 1  # Top border
        row_range.api.Borders(9).LineStyle = 1  # Bottom border
        row_range.api.Borders(7).LineStyle = 1  # Left border
        row_range.api.Borders(10).LineStyle = 1  # Right border    

    for col in columns_to_format:
        if col == 'total_round':
            used_range_C.formula = used_range_C.formula
            used_range_C.number_format = "0"

        else:
            used_range_D.formula = used_range_D.formula
            used_range_D.number_format = "0"

    ws.api.Columns.AutoFit()
    Report_wb.save(Report_path + Report_save_name + '_' + formated_date + '.xlsx')
    Report_wb.close()
    xl_app.quit()

    my_zip = zipfile.ZipFile(Report_path + Report_save_name + '_' + formated_date + '.xlsx' + '.zip','w')
    my_zip.write(Report_path + Report_save_name + '_' + formated_date + '.xlsx', compress_type=zipfile.ZIP_DEFLATED, arcname=Report_save_name + '_' + formated_date + '.xlsx')
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
        zip_attachment_path = Report_path + Report_save_name + '_' + formated_date + '.xlsx' + '.zip'
        message.Attachments.Add(Source=zip_attachment_path)
    else:
        excel_attachment_path = Report_path + Report_save_name + '_' + formated_date + '.xlsx'
        message.Attachments.Add(Source=excel_attachment_path)

    if draft_mail == 0:
        message.Display()
        time.sleep(2)
        message.Send()
    else:
        message.Display()
        time.sleep(2)
        message.Display()
    
else:
    outlook = win32com.client.Dispatch('outlook.application')
    message = outlook.CreateItem(0)
    message.To = external_TO_list
    message.CC = external_CC_list
    message.Subject = '<Failed :>' + Report_save_name + ' ||'+  str(formated_date)
    mailBody = '<div style="font-size:15px;">Hi Team,</div>'
    mailBody += '<div>&nbsp;</div>'
    mailBody += f'<div style="font-size:15px;">Report <b>{Report_save_name}</b> is <b style="background-color:orange;">Failed</b> due to Data is not updated on ' + f'<font color="Purple"><i>{str(formated_day)}</i></font>' + '.'
    mailBody += '<div>&nbsp;</div>'
    mailBody += '<div style="font-size:15px;">Below is the summary of failure :'

    html = '<html><body><table border="1" cellspacing="2" cellpadding="1" ><tr><th>Table</th><th>Status</th><th>Remark</th></tr>'

    for index, row in Validation_check.iterrows():
        if Validation.get(row['Table_Name']) != pd.to_datetime(new_date):
            Table = row['Table_Name']
            Status =  'Failed'
#            Remark = 'Last Updated on : ' + str(Validation.get(row['Table_Name']).strftime("%d-%b-%Y"))
            Remark = 'Last Updated on : ' + datetime.strptime(Validation.get(row['Table_Name']), "%Y-%m-%d").strftime("%d-%b-%Y")
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
