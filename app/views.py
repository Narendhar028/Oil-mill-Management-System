from django.shortcuts import render,redirect,get_object_or_404
from . models import *
from django.contrib import messages
import datetime
from django.db.models import Q
from django.db import connection
import random 
from django.db.models import Sum, Count
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
import datetime
def home(request):
	a = Product.objects.all().order_by('-id')
	comment =Feedback.objects.all().order_by('-id')
	return render(request,'index.html',{'a':a,'comment':comment})
def register(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		address = request.POST.get('address')
		mobile= request.POST.get('mobile')
		email = request.POST.get('email')
		password = request.POST.get('password')
		fname = request.POST.get('fname')
		lname = request.POST.get('lname')
		country = request.POST.get('country')
		city = request.POST.get('city')
		zip = request.POST.get('zip')
		crt = Register_Detail.objects.create(username=username,
		address=address,mobile=mobile,password=password,email=email,fname=fname,lname=lname,
		city=city,country=country,zip=zip)
		if crt:
			messages.success(request,'Registered Successfully')
	return render(request,'register.html',{})
def dashboard(request):
	return render(request,'dashboard.html',{})
def add_category(request):
	if request.method == 'POST':
		a=request.POST.get('name')
		b = request.POST.get('con')
		post=Category.objects.create(name=a,description=b)
		messages.success(request,'Category Added Successfully')
	return render(request,'add_category.html',{})
def category(request):
	a=Category.objects.all()
	return render(request,'category.html',{'b':a})
def add_product(request):
	a=Category.objects.all()
	if request.method == 'POST':
		a=request.POST.get('name')
		b=request.POST.get('price')
		c=request.POST.get('category')
		d=request.POST.get('con')
		f =request.FILES['pic']
		g=request.POST.get('option')
		stock = request.POST.get('stock')
		c_id=Category.objects.get(id=int(c))
		prt = Product.objects.create(name=a,price=b,category=c_id,note=d,image=f,option=g,stock=stock)
		if prt:
			messages.success(request,'Product Added Successfully')
	return render(request,'add_product.html',{'a':a})
def product_list(request):
	a=Product.objects.all().order_by('-id')
	return render(request,'product_list.html',{'b':a})
def stock(request):
	a=Product.objects.all().order_by('-id')
	return render(request,'stock.html',{'b':a})
def product_edit(request,pk):
	a=Product.objects.filter(id=pk)
	b = Category.objects.all()
	if request.method == 'POST':
		a=request.POST.get('name')
		b=request.POST.get('price')
		c=request.POST.get('category')
		d=request.POST.get('con')
		stock = request.POST.get('stock')
		c_id=Category.objects.get(id=int(c))
		prt = Product.objects.filter(id=pk).update(name=a,price=b,category=c_id,note=d,stock=stock)
		if prt:
			return redirect('product_list')
	return render(request,'product_edit.html',{'value':a,'b':b})
def product_delete(request,pk):
	a=Product.objects.filter(id=pk).delete()
	return redirect('product_list')
def user_login(request):
	if request.session.has_key('username'):
		return redirect("user_dashboard")
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =  request.POST.get('password')
			post = Register_Detail.objects.filter(username=username,password=password)
			if post:
				username = request.POST.get('username')
				request.session['username'] = username
				a = request.session['username']
				sess = Register_Detail.objects.only('id').get(username=a).id
				request.session['user_id']=sess
				return redirect("user_dashboard")
			else:
				messages.success(request, 'Invalid Username or Password')
	return render(request,'login.html',{})
def user_dashboard(request):
	if request.session.has_key('username'):
		return render(request,'user_dashboard.html',{})
	else:
		return render(request,'login.html',{})
def logout(request):
	try:
		del request.session['username']
		del request.session['user_id']
	except:
		pass
	return render(request, 'login.html', {})
def products(request):
	a = Product.objects.all().order_by('-id')
	
	return render(request,'products.html',{'a':a})
def add_to_cart(request,pk):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		user_id = Register_Detail.objects.get(id=int(uid))
		product_id = Product.objects.get(id=int(pk))
		product_detail = Product.objects.filter(id=int(pk))
		if request.method == 'POST':
			price = request.POST.get('price')
			tot = request.POST.get('tot')
			a = int(tot)
			b = int(price)
			tot_price = a*b
			crt = Cart_Detail.objects.create(user_id=user_id,product_id=product_id,status='pending',
			quantity=tot,tot_price=tot_price)
			if crt:
				return redirect('view_items_cart_product')
		return render(request,'add_to_cart.html',{'product_detail':product_detail})
	else:
		return render(request,'login.html',{})
def remove_item(request,pk):
	Cart_Detail.objects.filter(id=int(pk)).delete()
	return redirect('view_items_cart_product')
def view_items_cart_product(request):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		r_num =  random.randrange(20, 50, 3)
		product_details = Cart_Detail.objects.filter(status='pending',user_id=int(uid))
		tot = Cart_Detail.objects.filter(status='pending',user_id=int(uid)).aggregate(Sum('tot_price'))
		return render(request,'view_items_cart_product.html',{'product_details':product_details,'tot':tot,'r_num':r_num})
	else:
		return render(request,'login.html',{})
def purchase(request):
    uid = request.session['user_id']
    order_id = request.GET.get('order_id')
    addr = Register_Detail.objects.filter(id=int(uid))
    
    if request.method == 'POST':
        # Update status of cart items to 'order' and link them to the purchased product
        cart_items = Cart_Detail.objects.filter(user_id=int(uid), status='pending')
        for cart_item in cart_items:
            # Retrieve the product associated with the cart item
            product = cart_item.product_id
            
            # Reduce the stock of the product by the quantity purchased
            product.stock -= cart_item.quantity
            
            # Save the updated stock value
            product.save()
            
            # Update status and date of the cart item
            cart_item.status = 'order'
            cart_item.book_id = order_id
            cart_item.date = timezone.now()
            cart_item.save()
        
        return redirect('order_item_user')
    
    return render(request, 'purchase.html', {'addr': addr})
def order_item_user(request):
	uid = request.session['user_id']
	cursor = connection.cursor()
	post = '''SELECT Sum(app_cart_detail.tot_price), app_cart_detail.book_id, app_cart_detail.date, app_cart_detail.status,
	app_cart_detail.user_id_id  from app_cart_detail where app_cart_detail.status='order' OR app_cart_detail.status='paid' AND 
	app_cart_detail.user_id_id = '%d' Group By app_cart_detail.book_id  '''  % (int(uid))
	query = cursor.execute(post)
	row = cursor.fetchall()
	return render(request,'order_item_user.html',{'product_details':row})
def purchased_item(request,pk,status):
	uid = request.session['user_id']
	product_details = Cart_Detail.objects.filter(book_id=pk,user_id=int(uid))
	tot = Cart_Detail.objects.filter(book_id=pk,user_id=int(uid)).aggregate(Sum('tot_price'))
	return render(request,'purchased_item.html',{'product_details':product_details,'tot':tot,'status':status})
def admin_login(request):
	if request.session.has_key('admin'):
		return redirect("add_category")
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =  request.POST.get('password')
			post = Admin_Detail.objects.filter(username=username,password=password)
			if post:
				username = request.POST.get('username')
				request.session['admin'] = username
				a = request.session['admin']
				sess = Admin_Detail.objects.only('id').get(username=a).id
				request.session['admin_id']=sess
				return redirect("add_category")
			else:
				messages.success(request, 'Invalid Username or Password')
	return render(request,'admin_login.html',{})
def admin_logout(request):
	try:
		del request.session['admin']
		del request.session['admin_id']
	except:
		pass
	return render(request, 'admin_login.html', {})
def admin_received_orders(request):
	cursor = connection.cursor()
	post = '''SELECT Sum(app_cart_detail.tot_price), app_cart_detail.book_id, app_cart_detail.date, app_cart_detail.status,
	app_cart_detail.user_id_id, u.username, u.email, u.mobile, app_cart_detail.id,Count(app_cart_detail.id) from app_cart_detail INNER JOIN 
	app_register_detail as u ON app_cart_detail.user_id_id=u.id Group By app_cart_detail.book_id '''
	query = cursor.execute(post)
	row = cursor.fetchall()
	return render(request,'admin_received_orders.html',{'product_details':row})
def detail(request,pk):
	product_details = Cart_Detail.objects.filter(book_id=pk)
	tot = Cart_Detail.objects.filter(book_id=pk).aggregate(Sum('tot_price'))
	return render(request,'details.html',{'product_details':product_details,'tot':tot})
def payment(request,pk):
	if request.method == 'POST':
		name = request.POST.get('delivery')
		pay = request.POST.get('payment')
		crt = Cart_Detail.objects.filter(book_id=pk).update(payment_status=pay,delivery_status=name,
		status='paid')
		if crt:
			messages.success(request,'Updated...')
	return render(request,'payment.html',{'detail':detail})
def single_product(request,pk):
	if request.session.has_key('user_id'):
		user_id = request.session['user_id']
		if request.method == 'POST':
			food_id = Product.objects.get(id=pk)
			uid = Register_Detail.objects.get(id=int(user_id))
			comment = request.POST.get('comment')
			rank = request.POST.get('rank')
			already_exist = Feedback.objects.filter(product_id=pk,user_id=int(user_id))
			if already_exist:
				messages.success(request,'You Already Comment.')
			else:
				crt = Feedback.objects.create(product_id=food_id,user_id=uid,comment=comment,rank=int(rank))
		comment_detail = Feedback.objects.filter(product_id=pk)
		tot = Feedback.objects.filter(product_id=pk).aggregate(Count('comment'))
		cnt = Feedback.objects.filter(product_id=pk).aggregate(Sum('rank'))
		row = Product.objects.filter(id=pk)
		return render(request,'single_product.html',{'row':row,'comment_detail':comment_detail,'tot':tot,'cnt':cnt})
	else:
		return render(request,'login.html',{})
def vendor_login(request):
	if request.session.has_key('vendor'):
		return redirect("vendor_dashboard")
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =  request.POST.get('password')
			post = Vendor_Detail.objects.filter(username=username,password=password)
			if post:
				username = request.POST.get('username')
				request.session['vendor'] = username
				a = request.session['vendor']
				sess = Vendor_Detail.objects.only('id').get(username=a).id
				request.session['vendor_id']=sess
				return redirect("vendor_dashboard")
			else:
				messages.success(request, 'Invalid Username or Password')
	return render(request,'vendor_login.html',{})
def vendor_dashboard(request):
	if request.session.has_key('vendor'):
		vendor_id = request.session['vendor_id']
		detail = Vendor_Product.objects.filter(vendor_id=int(vendor_id))
		return render(request,'vendor_dashboard.html',{'detail':detail})
	else:
		return render(request,'vendor_login.html',{})
def vendor_logout(request):
	try:
		del request.session['vendor']
		del request.session['vendor_id']
	except:
		pass
	return render(request, 'vendor_login.html', {})
def rise_invoice(request,pk):
	vendor_id = request.session['vendor_id']
	vid = Vendor_Detail.objects.get(id=int(vendor_id))
	product_id = Vendor_Product.objects.get(id=pk)
	if request.method == 'POST':
		a=request.POST.get('total_price')
		b=request.POST.get('rise_price')
		c=request.POST.get('edate')
		prt = Invoice.objects.create(edate=c,rise_price=b,total_price=a,vendor_id=vid,product_id=product_id,
		status='Pending Amount')
		if prt:
			return redirect(invoices)
	return render(request,'rise_invoice.html',{})
def invoices(request):
	vendor_id = request.session['vendor_id']
	detail = Invoice.objects.filter(vendor_id=int(vendor_id))
	return render(request,'invoices.html',{'detail':detail})
def lucky_cutomer(request):
	cursor=connection.cursor()
	sql='''SELECT app_register_detail.email, app_register_detail.username from app_register_detail ORDER BY RANDOM() '''
	post = cursor.execute(sql)
	row=cursor.fetchone()
	email = row[0]
	name = row[1]
	recipient_list = [email]
	email_from = settings.EMAIL_HOST_USER
	b = EmailMessage('LUCKY CUSTOMER ALERT','You Are Selected as Lucky Customer. Come and Meet Us... Cakes & Juice,Icecream Shop'  ,email_from,recipient_list).send()
	return render(request,'lucky_cutomer.html',{'name':name, 'email':email})