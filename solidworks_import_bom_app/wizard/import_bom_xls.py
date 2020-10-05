# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from io import BytesIO
import xlrd
import base64

logger = logging.getLogger(__file__)


class BomImportWizard(models.TransientModel):
    _name = 'bom.import.wizard'
    _description = "BOM Import Wizard"

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('bom.import.wizard'),
                                 required=True)

    importing_file = fields.Binary('Upload File', required=True)
    file_name = fields.Char('File Name')
    product_id = fields.Many2one('product.template', string='Product', required=True)

    def _create_bom_lines(self, products, root_bom):
        logger.debug('_create_bom_lines %s' % root_bom.id)
        for bom_line in products:
            logger.warning('_create_bom_lines creating %s' % bom_line['code'])

            product_ref = bom_line['code']
            product = self.env['product.product'].search([('default_code', '=', product_ref)], limit=1)
            logger.debug('_create_bom_lines found product %s' % product.id)
            self.env['mrp.bom.line'].create({
                'product_id': product.id,
                'product_qty': bom_line['qty'],
                'bom_id': root_bom.id
            })
            logger.debug('_create_bom_lines created bom line %s' % product.id)
            if len(bom_line['sub']) and product.bom_count == 0:
                logger.debug('_create_bom_lines creating sub for %s' % bom_line['code'])
                sub_bom = self.env['mrp.bom'].create({
                    'company_id': self.company_id.id,
                    'product_tmpl_id': product.product_tmpl_id.id,
                    'product_qty': 1,
                    'type': 'normal',
                })
                self._create_bom_lines(bom_line['sub'], root_bom=sub_bom)

    def custom_importbomfromxls_button(self):
        if not self.env.user.has_group('mrp.group_mrp_manager'):
            raise ValidationError(_(
                'Normal user is not completed this operation, this operation allow only for Manufacturing Manager...!'))

        if self.product_id.bom_count > 0:
            raise ValidationError('Selected product already has BoM')

        file_name = str(self.file_name)
        if self.importing_file:
            if '.' not in file_name:
                raise UserError(_('Please upload valid xls...!'))
            extension = file_name.split('.')[1]
            if extension not in ['xls', 'xlsx', 'XLS', 'XLSX']:
                raise UserError(_('Please upload only xls file.!'))

        inputx = BytesIO()
        inputx.write(base64.decodebytes(self.importing_file))
        book = xlrd.open_workbook(file_contents=inputx.getvalue())
        sheet = book.sheet_by_index(0)

        # Check missing products
        missing_products = set()
        corrupted_lines = set()
        for bom_line_n in range(1, sheet.nrows):

            if not all(
                (
                    len(str(sheet.cell(bom_line_n, 0).value)),
                    len(str(sheet.cell(bom_line_n, 1).value)),
                    len(str(sheet.cell(bom_line_n, 3).value)),
                )
            ):
                corrupted_lines.add(str(bom_line_n + 1))

            product_ref = sheet.cell(bom_line_n, 1).value.strip()
            product = self.env['product.template'].search([('default_code', '=', product_ref)], limit=1)
            if not product:
                missing_products.add(product_ref)

        if len(missing_products):
            raise UserError('Missing products for references:\n%s' % '\n'.join(missing_products))

        if len(corrupted_lines):
            raise UserError('Some line are corrupted:\n%s' % '\n'.join(corrupted_lines))

        bom_hierarchy = []
        stack = [bom_hierarchy]
        for bom_line_n in range(1, sheet.nrows):
            seq = str(sheet.cell(bom_line_n, 0).value).strip()
            if seq.endswith('.0'):
                seq = seq[:-2]
            numbers = seq.split('.')
            d = {
                'code': str(sheet.cell(bom_line_n, 1).value).strip(),
                'qty': str(sheet.cell(bom_line_n, 3).value).strip(),
                'sub': []
            }
            while len(numbers) < len(stack):
                stack.pop()
            while len(numbers) > len(stack):
                stack.append(stack[-1][-1]['sub'])
            stack[-1].append(d)

        root_bom = self.env['mrp.bom'].create({
            'company_id': self.company_id.id,
            'product_tmpl_id': self.product_id.id,
            'product_qty': 1,
            'type': 'normal',
        })
        logger.debug('CREATED ROOT BOM')
        self._create_bom_lines(bom_hierarchy, root_bom=root_bom)
