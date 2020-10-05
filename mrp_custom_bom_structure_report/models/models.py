# -*- coding: utf-8 -*-
import logging
from collections import Counter, defaultdict

from odoo import _, api, fields, models

logger = logging.getLogger(__name__)


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        res = super(ReportBomStructure, self)._get_bom(bom_id, product_id, line_qty, line_id, level)

        res['work_sum'] = res['bom'].x_studio_totalsum * res['bom_qty']
        res['work_time'] = res['bom'].x_studio_time
        res['total_work_sum'] = res['work_sum'] + sum([l['work_sum'] + l['sub_work_sum'] for l in res['components']])
        all_workshop = [d['workshop_time'] for d in res['components']]
        all_workshop.append({res['bom'].x_studio_workshop.id: res['work_time']})
        res['workshop_time'] = dict(sum((Counter(dict(x)) for x in all_workshop), Counter()))
        res['workshop_total_time'] = sum(res['workshop_time'].values())

        logger.warning(res)
        return res

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components, total = super(ReportBomStructure, self)._get_bom_lines(bom, bom_quantity, product, line_id, level)

        workshop_time_dict = defaultdict(lambda: 0)

        def _get_sub_line_work_sum(_child_bom, _qty, _workshop_time_dict):
            _sub_work_sum = 0
            for _line in _child_bom.bom_line_ids:
                if _line.child_bom_id:
                    factor = _line.product_qty * _qty
                    _workshop_time_dict[_line.child_bom_id.x_studio_workshop.id] += _line.child_bom_id.x_studio_time
                    _sub_work_sum += _line.child_bom_id.x_studio_totalsum * factor
                    _sub_work_sum += _get_sub_line_work_sum(_line.child_bom_id, factor, _workshop_time_dict)
            return _sub_work_sum

        for line in components:
            child_bom_id = line.get('child_bom')
            work_sum, sub_work_sum = 0, 0
            if child_bom_id:
                child_bom = self.env['mrp.bom'].browse(child_bom_id)

                workshop_time_dict[child_bom.x_studio_workshop.id] += child_bom.x_studio_time
                work_sum = child_bom.x_studio_totalsum * line['prod_qty']
                sub_work_sum = _get_sub_line_work_sum(child_bom, line['prod_qty'], workshop_time_dict)

            line['work_sum'] = work_sum
            line['sub_work_sum'] = sub_work_sum
            line['workshop_time'] = dict(workshop_time_dict)

        return components, total
