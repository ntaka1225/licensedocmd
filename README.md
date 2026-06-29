# licensedocmd
This program is designed to read data from a specified sheet within a designated Excel file and generate license text files to fulfill the notice/attribution obligations of OSS licenses.

---
## Test
### Unit Test (model/controller)
- python test_runner.py

### Output text file from dummy data (default is text format option)
- python __main__.py --test
- python __main__.py --test [format]

---
## Running
- python __main__.py <filename> <sheetname> [format]

### options
| Option | Description | Required | Default |
|---|---|---|---|
| filename | input file | yes | - |
| sheetname | read sheet | yes | - |
| format | output text format | no | default |

### e.x
- python __main__.py oss_list.xlsx listsheet 
- python __main__.py oss_list.xlsx listsheet default

---
## ToDo
- Enhance formatting options (Consolidate duplicate license texts)
- Enable configuration of Excel column mappings (Load via a config file)
