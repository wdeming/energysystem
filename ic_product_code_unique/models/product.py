# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
          
    @api.constrains('default_code')
    def _check_unique_constraint(self):
        for rec in self:
            record = rec.search([('default_code', '=ilike', rec.default_code),('id','!=',rec.id)])
            if record:
                raise ValidationError(_('Another product with the same code exists!'))
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res.default_code = res.default_code.rstrip().lstrip()
        return res
    
    def write(self, vals):
        if 'default_code' in vals:
            vals['default_code'] = vals['default_code'].rstrip().lstrip()
        return super(ProductTemplate, self).write(vals)
		