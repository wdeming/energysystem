# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


def _flatten_bom_products(lines):
    products_dict = defaultdict(lambda: 0)
    for line in lines:
        if not line.child_line_ids:
            products_dict[line.product_id] += line.product_qty
        for _sub_product, _sub_qty in _flatten_bom_products(line.child_line_ids).items():
            products_dict[_sub_product] += _sub_qty
    return products_dict


class MrpEco(models.Model):
    _inherit = "mrp.eco"

    def action_create_rfq(self):
        self.ensure_one()

        if not self.bom_id:
            raise UserError('Не выбран BoM')

        products_dict = _flatten_bom_products(self.bom_id.bom_line_ids)

        purchase_order_values = {
            'name': 'New',
            'partner_id': 1,
            'from_plm': True,
            'source_plm_id': self.id,
            'date_planned': fields.Date.today(),
            'order_line': [
                (0, 0, {
                    'product_id': _product.id,
                    'name': _product.name,
                    'product_qty': _qty,
                    'price_unit': _product.standard_price,
                    'product_uom': _product.uom_id.id,
                    'product_uom_qty': _qty,
                }) for _product, _qty in products_dict.items()
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
