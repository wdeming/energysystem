# -*- coding: utf-8 -*-

{
	'name':"Import BOM From excel file (Solidworks)",
	'author': "Colibri",
	'version' : '13.0.1.0',
	'description':"""Import BOM From excel file (Solidworks)""",
	"license" : "OPL-1",
	'depends':['base','sale_management','account','stock','mrp'],
	'data':[
			'wizard/import_bom_xlsfile.xml',
			],
	'installable':True,
	'auto_install':False,
	'category' : 'Manufacturing',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
