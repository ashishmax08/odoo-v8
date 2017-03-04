# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp.http import request,Response
from openerp.exceptions import Warning 
import json
import logging
import jwt
from datetime import datetime,timedelta
_logger = logging.getLogger(__name__)

exp = datetime.now() + timedelta(minutes=10)

SECRET = "GOD_BLESS_ME"
algorithm = 'HS256'
class Api1(http.Controller):

		d =[]
		@http.route('/odoo/test', type='json',auth='public', methods=['POST'], website=True)
		def json_test(self, **args):
			_logger.info('CONNECTION SUCCESSFUL')
			_logger.info(args)
			name = args.get('name', False)
			email = args.get('email', False)
			_logger.info(name)
			_logger.info(email)
			if not name:
					Response.status = '400 Bad Request'
			return name,email

		@http.route('/double/<int:num>/',type='http',auth='public')
		def double(self,num):
				n = num * 2
				return n

#api for user register
		@http.route('/api/register/', type='json', auth='public',methods=['POST'],website=True)
		def register(self,**args):
			_logger.info('CONNECTION SUCCESSFUL')

			partner_id = args.get('partner_id',False)
			name = args.get('name',False)
			company_id = 1
			display_name = args.get('name',False)
			email = args.get('email',False)
			

			supplier = False
			is_company = False
			customer = True
			employee = False
			active = True
			notify_email = 'always'
			zip = args.get('zip',False)
			country_id = 105
			street = args.get('street',False)
			city = args.get('city',False)
			mobile = args.get('mobile',False)

			obj = request.env['res.partner'].sudo()#this will give superuser rights to all the actions performed on this model
			_logger.info('CONNECTION SUCCESSFUL 1')
			obj = obj.search([('id','=',partner_id)])
			_logger.info('CONNECTION SUCCESSFUL 2')

			pid = obj.write({'name':name,'company_id':company_id,'display_name':display_name,'email':email,'supplier':supplier,
				'is_company':is_company,'customer':customer,'employee':employee,'active':active,'notify_email':notify_email,
				'zip':zip,'country_id':country_id,'street':street,'city':city,'mobile':mobile})
			_logger.info('CONNECTION SUCCESSFUL 3')
			return obj.id,obj.name,obj.country_id.name
#api for customer purchase history

		@http.route('/api/history/<string:email>',method='get',auth='public',type='http',website=True)
		def purchase_history(self,email,**args):

			d =[]
			#phone = args.get('phone',False)
			#_logger.info(phone)
			pid = request.env['res.partner'].sudo().search([('email','ilike', email)])[0].id#make fileld searcheable in base module
			_logger.info(pid)

			oid = request.env['sale.order'].sudo().search([('partner_id','=',pid)])
			for ids in oid:
				products = request.env['sale.order.line'].sudo().search([('order_id','=',ids.id)])
				for value in products:
					dic = {'id':value.id,'name':value.name,'price':value.price_unit,'qty':value.product_uom_qty,'amount':value.product_uom_qty*value.price_unit,'date_order':ids.date_order}
					d.append(dic)

			return json.dumps(d)
#api for fetching list of customers

		@http.route('/api/customer',method='get',type='http',auth='user')
		def customer_list(self,**args):
			_logger.info(request.uid)
			d= []
			cid = request.env['res.partner'].search([])
			for i in cid:
				dic = {'id':i.id,'name':i.name,'email':i.email,'phone':i.phone}
				d.append(dic)


			return json.dumps(d)
#api for pushing sale order

		@http.route('/api/sale_order',method='post',type='json',auth='public')
		def slae_order(self,**args):

			d = []


			partner_id = args.get('partner_id',False)
			section_name = args.get('section_name',False)
			token = args.get('token',False)

			try:
				decoded = jwt.decode(token,SECRET,algorithm)
			except jwt.InvalidTokenError as e:
				return e.message


			obj = request.env['sale.order'].sudo()
			section = request.env['crm.case.section'].sudo().search([('name','ilike',section_name)])
			order_id = obj.create({
				'partner_id':partner_id,
				'company_id':1,
				'state':'draft',
				'user_id':1,
				'section_id':section.id,
				'pricelist_id':1,
				'partner_invoice_id':partner_id,
				'partner_shipping_id':partner_id,
				'order_policy':'manual',
				'picking_policy':'direct',
				'warehouse_id':1,
				'shipped':False
				})

			_logger.info("order id")
			_logger.info(order_id)

			product_id = args.get('product_id',False)

			obj = request.env['sale.order.line'].sudo()

			for ids in product_id:

				pid = request.env['product.product'].sudo().search([('product_tmpl_id','=',ids['id'])])

				line_id = obj.create({
				'product_uos_qty':ids['qty'],
				'product_uom_qty':ids['qty'],
				'product_uom':ids['uom'],
				'sequence':10,
				'invoiced':False,
				'company_id':1,
				'order_id':order_id.id,
				'product_id':pid.id,
				'salesman_id':1,
					})

				d.append(line_id.id)


			return order_id.id,order_id.name,d

#api for login
		@http.route('/api/login',method='post',type='json',auth='public')
		def login(self,**kw):

			d=[]

			login = kw.get('login',False)
			pwd = kw.get('password',False)
			_logger.info(pwd)
			_logger.info(login)

			dic = {'login':login,'pwd':pwd,'iss':'zenerp.com','exp':exp}

			uid = request.session.authenticate(request.session.db, login, pwd)
			token = jwt.encode(dic,SECRET,algorithm)
			
			if uid:
				_logger.info(uid)
				info = request.env['res.users'].sudo().search([('id','=',uid)])
				
				_logger.info(info.id)
				_logger.info(info.name)
				dic = {"user_id":info.id,'name':info.name,'partner_id':info.partner_id.id}

				return {'message':'Login Successful',"user_id":info.id,'name':info.name,'partner_id':info.partner_id.id,'token':token}
			else:
				return {'message':"Invalid Id-password pair"}

#api for new user signup
		@http.route('/api/signup',method='post',type='json',auth='public')
		def signup(self,**kwargs):

			email = kwargs.get('email',False)
			name = kwargs.get('name',False)
			pwd = kwargs.get('password',False)

			obj=request.env['res.partner'].sudo()
			try:
				pid = obj.create({'name':name,'notify_email':'always','email':email})
			except (Warning,except_orm) as e:
				return e

			
			obj = request.env['res.users'].sudo()
			
			alias_obj = request.env['mail.alias'].sudo()
			alias_id = alias_obj.create({'alias_contact':'everyone','alias_defaults':'{}','alias_model_id':93,'alias_parent_model_id':93,'alias_name':name})
			uid = obj.create({'login':email,'password':pwd,'company_id':1,'partner_id':pid.id,'alias_id':alias_id.id})

			return {'user_id':uid.id,'partner_id':pid.id,'message':'user registered successfully'}

#api for password reset
		@http.route('/api/reset_password',type='json',method='post',auth='public')
		def password_reest(self,**args):
			email = args.get('email',False)

			obj = request.env['res.users'].sudo().search([('email','=',email)])

			if obj.exists():
				try:
					res_users = request.registry.get('res.users')
					res_users.reset_password(request.cr, openerp.SUPERUSER_ID, email)
				except Exception:
					return "Mail Delivery Failed"

			else:
				return "Email does not exist"

			return "An email has been sent with credentials to reset your password"

			
		@http.route('/api/context',method='post',type='json',website=True)
		def context_data(self,**kwargs):
			context = request.context.copy()
			return context
			'''context['uid'] = 4
			request.env.context = context
			#return request.redirect('/shop/cart/update')
			request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id), add_qty=float(add_qty), set_qty=float(set_qty))

			return request.redirect('/shop/cart')'''

		@http.route('/api/offers',method='get',type='http')
		def offer_image(self):
			d=[]
			obj = request.env['ecom_offers']
			ids = obj.search([])

			for i in ids:
				if (i.offer_type == 'banner'):
					image_url = '/website/image/ecom_offers/%s/image_banner' % i.id
					dic = {'id':i.id,'name':i.name,'image':image_url,'type':i.offer_type}
					d.append(dic)
				elif (i.offer_type == 'offer'):
					image_url = 'website/image/ecom_offers/%s/image' % i.id
					dic = {'id':i.id,'name':i.name,'code':i.offer_code,'image':image_url,'type':i.offer_type}
					d.append(dic)
			return json.dumps(d)

		@http.route('/api/verify_code',method='post',type='json',auth='public')
		def offer_code_verify(self,**kwargs):

			code = kwargs.get('code',False)
			product_id = kwargs.get('product_id',False)
			token = kwargs.get('token',False)

			try:
				decoded = jwt.decode(token,SECRET,algorithm)
				_logger.info("token printed")
				_logger.info(decoded)

			except jwt.InvalidTokenError as e:
				_logger.info('token error')
				return e.message

			d = []
			

			try:
				obj = request.env['ecom_offers'].sudo().search([('offer_code','ilike',code)])
			except:
				return {'message':'Server Error'}

			if obj.exists():


				if obj.product_id:
					for ids in product_id:
						if (obj.product_id.id  == ids['id'] and ids['qty'] >= obj.min_qty):
							dic = {'id':ids['id'],'discount %':obj.disc,'message':'ok'}
							d.append(dic)
						else:
							dic = {'id':ids['id'],'discount %':0.00,'message':'product not suitable for coupon code/check minimum quantity required'}
							d.append(dic)
					return d,request.session.uid


				elif obj.product_category:

					self.cat_listing(obj.product_category.id)

					for ids in product_id:
						cat_id = request.env['product.template'].search([('id','=',ids['id'])])[0]


						if (cat_id.public_categ_ids.id in self.d) and (ids['qty'] >= obj.min_qty):
							dic = {'id':ids['id'],'discount %':obj.disc,'message':'ok'}
							d.append(dic)
						else:
							dic = {'id':ids['id'],'discount %':0.00,'message':'product not suitable for coupon code/check minimum quantity required'}
							d.append(dic)
					

					return d

			else:
				return {'message':'Invalid code'}

		@http.route('/api/logout',type='http')
		def user_logout(self):
			if not request.session.uid:
				return "Please login"
			try:
				request.session.logout(keep_db=True)
			except:
				return "Error in logout,Try Again"
			return "User logged out successfully"


		def cat_listing(self,cid):
			obj = request.env['product.public.category'].search([('id','=',cid)])
			
			if obj.child_id:
				for j in obj.child_id:
					self.cat_listing(j.id)
			else:
				self.d.append(cid)

			return self.d



