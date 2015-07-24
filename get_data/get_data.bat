set mongopath=C:\Progra~1\MongoDB\Server\3.0\bin

@echo Downloading latest data...
python download_all.py

@echo Drop existing table and insert that data into the collections
@echo Data does not have uniqe _id fields so updating tables is impossible
%mongopath%\mongoimport.exe respondent_id_list.json /drop
%mongopath%\mongoimport.exe responses.json /drop
%mongopath%\mongoimport.exe survey_details.json /drop
%mongopath%\mongoimport.exe survey_ids.json /drop

echo updating the session_table from those collections
c:\Python27\python.exe ..\build_5th_table.py