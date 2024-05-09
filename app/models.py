from django.db import models
from django.utils import timezone
class Category(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=1000,null=True)
	def __str__(self):
		return self.name
class Product(models.Model):
	name = models.CharField(max_length=50)
	price = models.CharField(max_length=50)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	note = models.TextField(max_length=2000)
	image = models.FileField('Upload Image',upload_to='documents/',null=True)
	option = models.CharField(max_length=100,null=True)
	stock = models.IntegerField(null=True,blank=True)
	def __str__(self):
		return self.name
class Register_Detail(models.Model):
	username = models.CharField(max_length=50,unique=True)
	fname = models.CharField(max_length=50)
	lname = models.CharField(max_length=50)
	address = models.CharField(max_length=50)
	mobile = models.CharField(max_length=20)
	password = models.CharField(max_length=50)
	email = models.EmailField(max_length=50)
	country = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	zip = models.CharField(max_length=50)
	def __str__(self):
		return self.username
class Cart_Detail(models.Model):
	user_id = models.ForeignKey(Register_Detail, on_delete=models.CASCADE)
	book_id = models.CharField(max_length=30,null=True)
	product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
	status = models.CharField(max_length=50)
	quantity = models.IntegerField()
	tot_price = models.CharField(max_length=200)
	date = models.DateField(default=timezone.now())
	delivery_status = models.CharField(max_length=100,null=True,blank=True)
	payment_status = models.CharField(max_length=100,null=True,blank=True)
	def __str__(self):
		return self.product_id.name
	def publish(self):
		self.date = timezone.now()
		self.save()
class Admin_Detail(models.Model):
	username = models.CharField(max_length=30)
	email = models.EmailField(max_length=30)
	mobile = models.CharField(max_length=30)
	country = models.CharField(max_length=30)
	address = models.CharField(max_length=200)
	city = models.CharField(max_length=30)
	password = models.CharField(max_length=200)
	def __str__(self):
		return self.username
class Feedback(models.Model):
	product_id =  models.ForeignKey(Product, on_delete=models.CASCADE)
	user_id =  models.ForeignKey(Register_Detail, on_delete=models.CASCADE)
	comment = models.CharField(max_length=30)
	rank =  models.IntegerField()
	date = models.DateField('Posted Date',default=timezone.now())
	def __str__(self):
		return self.product_id.name
	def publish(self):
		self.date = timezone.now()
		self.save()
