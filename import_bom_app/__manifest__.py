# -*- coding: utf-8 -*-

{
	'name':"Import BOM From excel-CSV file",
	'author': "Edge Technologies",
	'version' : '13.0.1.0',
	'live_test_url':'https://youtu.be/Dgr23V0HsXA',
	"images":["static/description/main_screenshot.png"],
	'summary':"Apps for Import BOM import bill of materials import bom from excel import bom from csv import from xls file import bom data import bill of material from excel import bill of material data easy to import bom by csv",
	'description':"""Import Multiple data from XLS and CSV files with & without variants""",
	"license" : "OPL-1",
	'depends':['base','sale_management','account','stock','mrp'],
	'data':[
			'wizard/import_bom_xlsfile.xml',
			],
	'installable':True,
	'auto_install':False,
	'price': 10,
	'category' : 'Manufacturing',
	'currency': "EUR",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
