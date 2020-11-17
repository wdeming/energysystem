# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_create_rfq(self):
        self.ensure_one()

        purchase_lines = self.order_line.filtered(
            lambda p: not self.env['mrp.bom']._bom_find(product_tmpl=p.product_template_id)
        )

        if not purchase_lines:
            raise UserError('You have no purchase items in this order')

        purchase_order_values = {
            'name': 'New',
            'partner_id': 1,
            'from_sales': True,
            'source_sale_order_id': self.id,
            'date_planned': fields.Date.today(),
            'order_line': [
                (0, 0, {
                    'product_id': _line.product_id.id,
                    'name': _line.product_id.name,
                    'product_qty': _line.product_uom_qty,
                    'price_unit': _line.price_total,
                    'product_uom': _line.product_uom.id,
                    'product_uom_qty': _line.product_uom_qty,
                }) for _line in purchase_lines
            ]
        }

        self.env['purchase.order'].create(purchase_order_values)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'RFQ создан',
                'type': 'rainbow_man',
            }
        }
