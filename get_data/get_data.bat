set mongopath=C:\Progra~1\MongoDB\Server\3.0\bin

@echo Downloading latest data...
c:\Python27\python.exe download_all.py

@echo Insert that data into the collections
%mongopath%\mongoimport.exe respondent_id_list.json
%mongopath%\mongoimport.exe responses.json
%mongopath%\mongoimport.exe survey_details.json
REM %mongopath%\mongoimport.exe survey_ids.json /drop

echo updating the session_table from those collections
c:\Python27\python.exe ..\build_5th_table.py