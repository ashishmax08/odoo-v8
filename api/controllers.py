# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
import json
import logging
_logger = logging.getLogger(__name__)

class Api(http.Controller):

	d = []
	@http.route('/api/api/', auth='public')
	def index(self, **kw):
		return "Hello, world"

	@http.route('/api/product/cid=<int:pid>/',auth='public',type='http',method='get')
	def prod_fetch(self, pid):
		d =[]
		prod = request.env['product.template'].search([('create_uid','=', pid)])
		_logger.info(prod)
		for value in prod:
			dic =  {"id":value.id,"name":value.name,"desc":value.description,"image":value.image_small,'uom_id':value.uom_id.id}
			d.append(dic)
		return json.dumps(d)

	@http.route('/api/auto_search/<name>',auth='public',type='http',method='get')
	def auto_search(self,name):
		d=[]
		prod = request.env['product.template'].search([('name','=ilike', name+'%')])
		for value in prod:
			dic = {'id':value.id,'name':value.name}
			d.append(dic)
		return json.dumps(d)

	@http.route('/api/search/<int:id>',auth='public',type='http',method='get')
	def search(self,id):
		d=[]
		prod = request.env['product.template'].search([('id','=', id)])

		for value in prod:
			dic = {'id':value.id,'name':value.name,'quant':value.qty_available}
			d.append(dic)
		return json.dumps(d)

	@http.route('/api/cat_list',type="http",method="get",auth='public')
	def cat_list(self):
		d=[]
		
		obj = request.env['product.public.category'].search([])

		for i in obj:
			f = []
			for j in i.child_id:
				#child = {'child_id':j.id}
				f.append(j.id)

			image_url = '/website/image/product.public.category/%s/image' % (i.id)
			dic = {'id':i.id,'name':i.name,'image_url':image_url,'parent_id':i.parent_id.id,'child_id':f}
			d.append(dic)

		return json.dumps(d)

	@http.route('/api/category/id=<int:cid>',auth='public',type='http',method='get')
	def category(self,cid):

		self.d = []
		self.ids_list(cid)
		
		d =[]
		'''count = request.env['product.public.category'].search_count([('parent_id','=',cid)])
		if count >0:
			obj = request.env['product.public.category'].search([('parent_id','=',cid)])
			for i in obj:
				prod = request.env['product.template'].search([('public_categ_ids','=',i.id)])
				for value in prod:
					dic = {'id':value.id,'name':value.name}
					d.append(dic)
			return json.dumps(d)'''


		for i in self.d:
			prod = request.env['product.template'].sudo().search([('public_categ_ids','=',i)])
			
			for value in prod:
				image_url = '/website/image/product.template/%s/image' % (value.id)
				dic = {'id':value.id,'name':value.name,'uom_id':value.uom_id.id,'sale_price':value.list_price,'pricelist':value.pricelist_id.id,'qty_aval':value.qty_available,'image':image_url,'tax_name':value.taxes_id.name,'tax_percent':value.taxes_id.amount * float(100.00)}
				d.append(dic)
		return json.dumps(d)



	def ids_list(self,cid):
		
		
		obj = request.env['product.public.category'].search([('parent_id','=',cid)])
		
		if not obj.exists():
			self.d.append(cid)
		else:
			for i in obj:
				count = request.env['product.public.category'].search_count([('parent_id','=',i.id)])
				if count > 0:
					self.d = self.ids_list(i.id)

				
				self.d.append(i.id)

		return self.d

	@http.route('/api/home',method='get',type='http',auth='public')
	def test_test(self):
		return "It Is Working !!!"


	
#     @http.route('/api/api/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('api.listing', {
#             'root': '/api/api',
#             'objects': http.request.env['api.api'].search([]),
#         })

#     @http.route('/api/api/objects/<model("api.api"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('api.object', {
#             'object': obj
#         })
