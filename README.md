# licensedocmd
This program is designed to read data from a specified sheet within a designated Excel file and generate license text files to fulfill the notice/attribution obligations of OSS licenses.

---
## Run the .exe file. 
- Move to the folder containing the .exe file.
  - cd [the folder containing the .exe]

- Run the .exe file.
  - python \_\_main\_\_.exe \<filenmae\> \<sheetname\> \<format\>

- e.x
  - python \_\_main\_\_.exe oss_list.xlsx listsheet 
  - python \_\_main\_\_.exe oss_list.xlsx listsheet default
  - python \_\_main\_\_.exe oss_list.xlsx listsheet aggregate

### options
| Option | Description | Required | Default |
|---|---|---|---|
| filename | input file | yes | - |
| sheetname | read sheet | yes | - |
| format | output text format<br># Unspecified = default<br># \'aggregate\' is aggregation(=old style) format | no | default |

---
## Run the script file. 
- Move to the folder containing the script file.
  - cd [the folder containing the script]
- Run the script file.
  - python \_\_main\_\_.py <filename> <sheetname> [format]

### e.x
- python \_\_main\_\_.py oss_list.xlsx listsheet 
- python \_\_main\_\_.py oss_list.xlsx listsheet default
- python \_\_main\_\_.py oss_list.xlsx listsheet aggregate

---
## Test
### Unit Test (model/controller)
- python test_runner.py

### Output text file from dummy data (default is text format option)
- python \_\_main\_\_.py --test
- python \_\_main\_\_.py --test [format]

---
## ToDo
- Enhance formatting options (Consolidate duplicate license texts)
- Enable configuration of Excel column mappings (Load via a config file)
