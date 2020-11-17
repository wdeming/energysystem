# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    from_plm = fields.Boolean('Created from PLM', default=False)
    from_sales = fields.Boolean('Created from Sales', default=False)

    source_plm_id = fields.Many2one('mrp.eco', 'Source PLM')
    source_sale_order_id = fields.Many2one('sale.order', 'Source Sale Order')
