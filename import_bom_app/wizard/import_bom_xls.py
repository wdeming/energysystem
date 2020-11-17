# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from io import BytesIO,StringIO
import xlrd
import base64
import io
import codecs
import csv

class BomImportWizard(models.TransientModel):
	_name = 'bom.import.wizard'
	_description = "BOM Import Wizard"

	company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env['res.company']._company_default_get('bom.import.wizard'),required=True)
	importing_method = fields.Selection(selection=[("with_var", "Import BOM With Variants"),("without_var", "Import BOM")], string="Import Options", required=True)
	importing_file = fields.Binary('Upload File',required=True)
	selection_csv_xls = fields.Selection(selection=[("select_csv", "CSV File"),("select_xls", "XLS File")], string="Import From",required=True)
	file_name = fields.Char('File Name')

	def custom_importbomfromxls_button(self):
		if not self.env.user.has_group('mrp.group_mrp_manager'):
			raise ValidationError(_('Normal user is not completed this operation, this operation allow only for Manufacturing Manager...!'))
		if self.selection_csv_xls == 'select_xls':
			file_name = str(self.file_name)
			if self.importing_file:
				if '.' not in file_name:
					raise UserError(_('Please upload valid xls...!'))
				extension = file_name.split('.')[1]
				if extension not in ['xls','xlsx','XLS','XLSX']:
					raise UserError(_('Please upload only xls file.!'))
				if self.importing_method == 'with_var':
					if file_name != 'sample_with_variant.xls':
						raise ValidationError(_('Please upload (sample_with_variant.xls) file..!'))

			inputx = BytesIO()
			inputx.write(base64.decodestring(self.importing_file))
			book = xlrd.open_workbook(file_contents = inputx.getvalue())
			sheet = book.sheet_by_index(0)
			d = {}
			for suits in range(1,sheet.nrows):
				if self.importing_method == 'with_var':
					if sheet.cell(suits, 0).value not in d:
						d.update({sheet.cell(suits, 0).value:{'Product':sheet.cell(suits, 1).value,
						'Product Variant':sheet.cell(suits, 2).value,'Quantity':sheet.cell(suits, 3).value,
						'Routing':sheet.cell(suits, 4).value,
						'Reference':sheet.cell(suits, 5).value,'BOM Type':sheet.cell(suits, 6).value,
						'Sequence':sheet.cell(suits, 7).value,
						'Manufacturing Readiness':sheet.cell(suits, 8).value,'Operation':sheet.cell(suits, 9).value,
						'Component':sheet.cell(suits, 10).value}})
						custom_product = self.env['product.template'].search([('name','=',d[sheet.cell(suits, 0).value]['Product'])])
						custom_product_component = self.env['product.product'].search([('name','=',d[sheet.cell(suits, 0).value]['Component'])],
							limit=1)
						custom_product_variants = self.env['product.product'].search([('default_code','=',d[sheet.cell(suits, 0).value]['Product Variant'])],
							limit=1)
						xls_bom = self.env['mrp.bom'].create({'company_id':self.company_id.id,'product_tmpl_id':custom_product.id,
							'product_id':custom_product_variants.id,
							'product_qty':d[sheet.cell(suits, 0).value]['Quantity'],
							'type':d[sheet.cell(suits, 0).value]['BOM Type'],
							'code':d[sheet.cell(suits, 0).value]['Reference'],'sequence':d[sheet.cell(suits, 0).value]['Sequence']})
						self.env['mrp.bom.line'].create({'product_id':custom_product_component.id,
							'product_qty':d[sheet.cell(suits, 0).value]['Quantity'],
							'bom_id':xls_bom.id})
					else:
						d[sheet.cell(suits, 0).value].update({'Product':sheet.cell(suits, 1).value,
						'Product Variant':sheet.cell(suits, 2).value,'Quantity':sheet.cell(suits, 3).value,
						'Routing':sheet.cell(suits, 4).value,
						'Reference':sheet.cell(suits, 5).value,'BOM Type':sheet.cell(suits, 6).value,
						'Sequence':sheet.cell(suits, 7).value,
						'Manufacturing Readiness':sheet.cell(suits, 8).value,'Operation':sheet.cell(suits, 9).value,
						'Component':sheet.cell(suits, 10).value})
						custom_product_components = self.env['product.product'].search([('name','=',d[sheet.cell(suits, 0).value]['Component'])],
							limit=1)
						self.env['mrp.bom.line'].create({'product_id':custom_product_components.id,
							'product_qty':d[sheet.cell(suits, 0).value]['Quantity'],
							'bom_id':xls_bom.id})

				elif self.importing_method == 'without_var':
					if sheet.cell(suits, 0).value not in d:
						d.update({sheet.cell(suits, 0).value:{'Product':sheet.cell(suits, 1).value
							,'Quantity':sheet.cell(suits, 3).value,
						'Routing':sheet.cell(suits, 4).value,
						'Reference':sheet.cell(suits, 5).value,'BOM Type':sheet.cell(suits, 6).value,
						'Sequence':sheet.cell(suits, 7).value,
						'Manufacturing Readiness':sheet.cell(suits, 8).value,'Operation':sheet.cell(suits, 9).value,
						'Component':sheet.cell(suits, 10).value}})
						custom_product = self.env['product.template'].search([('name','=',d[sheet.cell(suits, 0).value]['Product'])])
						custom_product_component = self.env['product.product'].search([('name','=',d[sheet.cell(suits, 0).value]['Component'])],
							limit=1)
						xls_bom = self.env['mrp.bom'].create({'company_id':self.company_id.id,'product_tmpl_id':custom_product.id,
							'product_qty':d[sheet.cell(suits, 0).value]['Quantity'],
							'type':d[sheet.cell(suits, 0).value]['BOM Type'],
							'code':d[sheet.cell(suits, 0).value]['Reference'],'sequence':d[sheet.cell(suits, 0).value]['Sequence']})
						self.env['mrp.bom.line'].create({'product_id':custom_product_component.id,
							'product_qty':d[sheet.cell(suits, 0).value]['Quantity'],
							'bom_id':xls_bom.id})

					else:
						d[sheet.cell(suits, 0).value].update({'Product':sheet.cell(suits, 1).value,
						'Quantity':sheet.cell(suits, 3).value,
						'Routing':sheet.cell(suits, 4).value,
						'Reference':sheet.cell(suits, 5).value,'BOM Type':sheet.cell(suits, 6).value,
						'Sequence':sheet.cell(suits, 7).value,
						'Manufacturing Readiness':sheet.cell(suits, 8).value,'Operation':sheet.cell(suits, 9).value,
						'Component':sheet.cell(suits, 10).value})
						custom_product_components = self.env['product.product'].search([('name','=',d[sheet.cell(suits, 0).value]['Component'])],
							limit=1)
						self.env['mrp.bom.line'].create({'product_id':custom_product_components.id,
							'product_qty':d[sheet.cell(suits, 0).value]['Quantity'],
							'bom_id':xls_bom.id})

		elif self.selection_csv_xls == 'select_csv':
			file_name = str(self.file_name)
			if self.importing_file:
				if '.' not in file_name:
					raise UserError(_('Please upload valid CSV file...!'))
				extension = file_name.split('.')[1]
				if extension not in ['csv','CSV']:
					raise UserError(_('Please upload only csv file.!'))
				if self.importing_method == 'with_var':
					if file_name != 'sample_with_variant.csv':
						raise ValidationError(_('Please upload (sample_with_variant.csv) file..!'))

			d1 = {}
			with io.BytesIO(base64.b64decode(self.importing_file)) as f:
				readers = csv.DictReader(codecs.iterdecode(f, 'utf-8'))
				for row in readers:
					if self.importing_method == 'with_var':
						if row['BOM ID'] not in d1:
							d1.update({row['BOM ID']:{'Product':(row['PRODUCT']),
							'Product Variant':(row['PRODUCT VARIANT']),'Quantity':(row['QUANTITY']),
							'Routing':(row['ROUTING']),
							'Reference':(row['REFERENCE']),'BOM Type':(row['BOM TYPE']),
							'Sequence':(row['SEQUENCE']),
							'Manufacturing Readiness':(row['MANUFACTURING READINESS']),'Operation':(row['OPERATION']),
							'Component':(row['COMPONENT'])}})
							custom_product = self.env['product.template'].search([('name','=',d1[row['BOM ID']]['Product'])])
							custom_product_component = self.env['product.product'].search([('name','=',d1[row['BOM ID']]['Component'])],
								limit=1)
							custom_product_variants = self.env['product.product'].search([('default_code','=',d1[row['BOM ID']]['Product Variant'])],
								limit=1)
							csv_bom = self.env['mrp.bom'].create({'company_id':self.company_id.id,'product_tmpl_id':custom_product.id,
								'product_id':custom_product_variants.id,
								'product_qty':d1[row['BOM ID']]['Quantity'],
								'type':d1[row['BOM ID']]['BOM Type'],
								'code':d1[row['BOM ID']]['Reference'],'sequence':d1[row['BOM ID']]['Sequence']})
							self.env['mrp.bom.line'].create({'product_id':custom_product_component.id,
								'product_qty':d1[row['BOM ID']]['Quantity'],
								'bom_id':csv_bom.id})
						else:
							d1[row['BOM ID']].update({'Product':(row['PRODUCT']),
							'Product Variant':(row['PRODUCT VARIANT']),'Quantity':(row['QUANTITY']),
							'Routing':(row['ROUTING']),
							'Reference':(row['REFERENCE']),'BOM Type':(row['BOM TYPE']),
							'Sequence':(row['SEQUENCE']),
							'Manufacturing Readiness':(row['MANUFACTURING READINESS']),'Operation':(row['OPERATION']),
							'Component':(row['COMPONENT'])})
							custom_product_components1 = self.env['product.product'].search([('name','=',d1[row['BOM ID']]['Component'])],
								limit=1)
							self.env['mrp.bom.line'].create({'product_id':custom_product_components1.id,
								'product_qty':d1[row['BOM ID']]['Quantity'],
								'bom_id':csv_bom.id})
					elif self.importing_method == 'without_var':
						if row['BOM ID'] not in d1:
							d1.update({row['BOM ID']:{'Product':(row['PRODUCT']),
							'Quantity':(row['QUANTITY']),
							'Routing':(row['ROUTING']),
							'Reference':(row['REFERENCE']),'BOM Type':(row['BOM TYPE']),
							'Sequence':(row['SEQUENCE']),
							'Manufacturing Readiness':(row['MANUFACTURING READINESS']),'Operation':(row['OPERATION']),
							'Component':(row['COMPONENT'])}})
							custom_product = self.env['product.template'].search([('name','=',d1[row['BOM ID']]['Product'])])
							custom_product_component = self.env['product.product'].search([('name','=',d1[row['BOM ID']]['Component'])],
								limit=1)
							csv_bom = self.env['mrp.bom'].create({'company_id':self.company_id.id,'product_tmpl_id':custom_product.id,
								'product_qty':d1[row['BOM ID']]['Quantity'],
								'type':d1[row['BOM ID']]['BOM Type'],
								'code':d1[row['BOM ID']]['Reference'],'sequence':d1[row['BOM ID']]['Sequence']})
							self.env['mrp.bom.line'].create({'product_id':custom_product_component.id,
								'product_qty':d1[row['BOM ID']]['Quantity'],
								'bom_id':csv_bom.id})
						else:
							d1[row['BOM ID']].update({'Product':(row['PRODUCT']),
							'Quantity':(row['QUANTITY']),
							'Routing':(row['ROUTING']),
							'Reference':(row['REFERENCE']),'BOM Type':(row['BOM TYPE']),
							'Sequence':(row['SEQUENCE']),
							'Manufacturing Readiness':(row['MANUFACTURING READINESS']),'Operation':(row['OPERATION']),
							'Component':(row['COMPONENT'])})
							custom_product_components1 = self.env['product.product'].search([('name','=',d1[row['BOM ID']]['Component'])],
								limit=1)
							self.env['mrp.bom.line'].create({'product_id':custom_product_components1.id,
								'product_qty':d1[row['BOM ID']]['Quantity'],
								'bom_id':csv_bom.id})
