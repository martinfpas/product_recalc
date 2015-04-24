# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>)
#    Copyright (C) 2013-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class account_product_cost_recalculation(osv.TransientModel):
    _name = "account.product.cost.recalculation"
    _description = "Recalculate Product Costs"

    _columns = {
        'period_id': fields.many2one('account.period', "Period", required=False,
                                     help="Period for which recalculation will be done."),
        'product_id': fields.many2one('product.product', "Product", domain=[('active', '=', True),
                                                                            ('cost_method', '=', 'standard'),
                                                                            ('type', '=', 'product')],
                                      required=False,
                                      help="Product for which recalculation will be done. If not set recalculation will be done for all products with cost method set 'Average Price'"),
    }
    _defaults = {
        'period_id': False,
        'product_id': False,
    }

    def _do_recalculation(self, cr, uid, ids, context=None):
        # array de productos en cero  #najdem ustrezne izdelke
        
        logging.info(" >>>>_do_recalculation>>>> ")
        _product_ids = []

        _product_ids = self.pool.get('product.product').search(cr, uid, [('active', '=', True),])

        # preraÄ�unam posamezen izdelek
        _products = self.pool.get('product.product').browse(cr, uid, _product_ids, context)
        
        i=0
        id=0
        
        for _product in _products:
            
            id = self.pool.get('purchase.order.line').search(cr,uid,[('product_id','=', _product.id)],order='date_order desc', limit=1)
            if(len(id) == 0):
                if(_product.standard_price == 0):
                    logging.info(" >>>>>>>>>>>>>>>>>>>>>>>>>> PRECIO CERO ! >>>>>>>>>>>>>>>>>>>>>>>>>> ")
                logging.info(_product.id)
                _product.write({'cost_method':'average'})
            else:
                 # TODO: QUITAR EL BROWSE DE ACA
                 order_line = self.pool.get('purchase.order.line').browse(cr, uid, id[0], context)
                 if order_line:
                     logging.info(" >>> order_line.price_unit >>>>> ")
                     logging.info(order_line.price_unit)
                     _product.write({'cost_method':'average', 'standard_price' : order_line.price_unit})
                 else:
                    logging.info(" >>>>>>>>>>>>>>>>>>>>>>>>>> order_line NULL ! >>>>>>>>>>>>>>>>>>>>>>>>>> ")
            logging.info(" >>>>>>>> ")
            logging.info(_product.id)
            logging.info(id)
            i+=1
            
            
            
            

        return True

    def execute(self, cr, uid, ids, context=None):
        logging.info(" >>>> Execute >>>> ")
        if context is None:
            context = {}
        if self._do_recalculation(cr, uid, ids, context):
            return {'type': 'ir.actions.act_window_close'}
        else:
            return False
