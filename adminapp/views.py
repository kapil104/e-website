# Create your views here.
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.conf import settings
from ecommerce.models import Customer,ProductDetail,ProductImage,Order
from django.views.decorators.csrf import csrf_exempt

#for logout
from django.contrib.auth import logout
import os
curl = settings.C_URL 
media_url=settings.MEDIA_URL

#for file uploading
from django.core.files.storage import FileSystemStorage

def sessioncheckadmin_middleware(get_response):
    def middleware(request):
        # print("============= request=====:",request.path)
        strpath = request.path
        list1 = strpath.split("/")
        if len(list1)>2:
            strnewpath = "/"+list1[1]+"/"+list1[2]+"/"
            if strnewpath=='C_URL/adminapp/' or strnewpath=='/adminapp/managecustomer/' or strnewpath=='/adminapp/addproduct/' or strnewpath == '/adminapp/addproductimage/' or strnewpath == '/adminapp/changepassword/' or strnewpath == '/adminapp/editprofile/'or strnewpath == '/adminapp/viewproduct/' or strnewpath == '/adminapp/deleteimage/' :
                if 'emailid' not in request.session: 
                            
                    response=redirect('http://localhost:8000/login')
                else:
                    response=get_response(request)
            else:
                response=get_response(request)
        else:
            return get_response(request)        
        return response
        
    return middleware 

def home(request):
    #==============session
    email=request.session.get("emailid")
    password =request.session.get("password")
    #==============session  
        
    qs=Customer.objects.filter(email=email,password=password)
    profile=qs.values()[0]
    return render(request,'AdminHome.html',{'C_URL':curl,"profile":profile})

def addproductimage(request):
    if request.method == "GET":
        qs=ProductDetail.objects.all().values("product_id","product_brand")
        print(qs)
        return render(request,'AddProductImage.html',{'C_URL':curl,"listofproduct":qs})
    
    elif request.method == "POST":
        
        product_id=request.POST.get("product_id")
        print(product_id)
        qs=ProductDetail.objects.all().values("product_id","product_brand")
        files = request.FILES.getlist('product_img')
        print(files,len(files))
        file_list = [] 
        msg=""
        try:              
            if files:
                for file in files:
                    print(file)
                    #for file uploading .............................
                    fs=FileSystemStorage()
                    fs.save(file.name,file)  
                    #......................................
                    new_file = ProductImage(product_img=file,product_id=product_id)
                    new_file.save()
                    file_list.append(new_file.product_img)
                msg="Product Images Uploaded Successfully"  
                return render(request,'AddProductImage.html',{'C_URL':curl,"msg":msg,'new_url':str(new_file.product_img),'list_img':file_list}) 
            else:
                msg="Plz Select Product Brand And Product Image!!"  
                return render(request,'AddProductImage.html',{'C_URL':curl,"listofproduct":qs,"msg":msg})

        except:
                msg="Product Images Not Uploaded!!"      
                return render(request,'AddProductImage.html',{'C_URL':curl,"listofproduct":qs})


def addproduct(request):
    if request.method == "GET":
        return render(request,'AddProduct.html',{'C_URL':curl})
    if request.method == "POST":
        product_brand = request.POST.get("product_brand")
        product_variant_name = request.POST.get("product_variant_name")
        product_sp = request.POST.get("product_sp")
        product_mrp = request.POST.get("product_mrp")
        product_discount = request.POST.get("product_discount")
        product_size = request.POST.get("product_size")
        product_description = request.POST.get("product_description")
        product_quantity = request.POST.get("product_quantity")
        product_color = request.POST.get("product_color")
        product_availability = request.POST.get("product_availability")
        print(product_brand,product_variant_name,product_sp,product_mrp,product_discount,product_size,product_description,product_quantity,product_color,product_availability)
        msg="Continue"

        if float(product_mrp) and float(product_discount) is not None:           
           product_sp = product_mrp - (product_mrp * product_discount / 100)

           return render(request,'AddProduct.html',{'C_URL':curl,"msg":msg ,"product_discount":product_discount})
        else:
            print("Don't any discount")
            try:
                obj = ProductDetail(product_brand=product_brand,product_variant_name=product_variant_name,product_sp=product_sp,product_mrp=product_mrp,product_discount=product_discount,product_size=product_size,product_description=product_description,product_quantity=product_quantity,product_color=product_color,product_availability=product_availability)
                obj.save()
                msg="Product Added Successfully"
            except Exception as e:
                print("Error while saving product:", e)
                msg="Product Not Added!"    
            return render(request,'AddProduct.html',{'C_URL':curl,"msg":msg})
    
def Logout(request):
    print("calling logout=============")
    logout(request)
    return redirect('http://localhost:8000/login/')


def managecustomer(request):
    customers=Customer.objects.filter(role="customer").values()
    print(customers)
    return render(request,'managecustomer.html',{'C_URL':curl,'customers':customers})

def managecustomerstatus(request):
    if request.method=="GET":
        id=request.GET.get('id')
        status=request.GET.get('status')
        print(id,status)
        if status == "0":
           Customer.objects.filter(customer_id=id).update(status=1)
           
        elif status == "1":
           Customer.objects.filter(customer_id=id).update(status=0)
          
        return redirect(curl+'adminapp/managecustomer/')    

def deletecustomer(request):
    if request.method=="GET":
        id=request.GET.get('id')
        print("Customer Id:",id)
        Customer.objects.filter(customer_id=id).delete()
        return redirect(curl+'adminapp/managecustomer/') 

def vieworders(request):
    id=request.GET.get('id')
    print("Customer Id:",id)
    orders = Order.objects.filter(customer_id=id).values()
    cust = Customer.objects.filter(customer_id=id).values()
    print(cust[0],"<=============")
    return render(request,'ViewOrders.html',{'C_URL':curl,"orderdetails":orders,"media_url":media_url,"customerdetails":cust[0]})

def viewproduct(request):
    if request.method == "GET":
        prod_details=ProductDetail.objects.all().values()
        print(prod_details)
        prod_img = ProductImage.objects.all().values("product_img","product_id")
        print(prod_img)
        prod_images=[] 
        for dic in prod_details:
            for imgdic in prod_img:
                if dic["product_id"] == imgdic["product_id"]:
                    prod_images.append(imgdic)
                    break
        print(prod_images)  
        return render(request,'ViewProduct.html',{'C_URL':curl,'prod_details':prod_details,'prod_images':prod_images,'media_url':media_url})
    
    
def delete_file(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
       os.remove(path)

def deleteproduct(request):
    if request.method=="GET":
        id=request.GET.get('id')
        print("Product Id:",id)
       
        prod_details=ProductDetail.objects.filter(product_id=id).values()
        print(prod_details)
        prod_img = ProductImage.objects.all().values("product_img","product_id")
        print(prod_img)

        # Instantiate FileSystemStorage
        fs = FileSystemStorage()
        for dic in prod_details:
            for imgdic in prod_img:
                if dic["product_id"] == imgdic["product_id"]:
                    # File name to delete
                    file_name = imgdic["product_img"]

                    # Delete the file
                    if fs.exists(file_name):
                        fs.delete(file_name)
                        print(f"File '{file_name}' deleted successfully.")
                    else:
                        print(f"File '{file_name}' does not exist.")

        ProductDetail.objects.filter(product_id=id).delete()

        return redirect(curl+'adminapp/viewproduct/')


    
def deleteimage(request):
    image_id = request.GET.get('id')
    if image_id:
        ProductImage.objects.filter(product_img_id=image_id).delete()
        
        return redirect('/adminapp/deleteimage/')
  
    images = ProductImage.objects.all()
    return render(request, 'deleteimage.html', {'images': images})


def changeproductdetail(request):
    if request.method == "GET":
        gId = request.GET.get('id')
        print("Get Product Image:", gId)

        #======= Product Detail & Images =======
        prod_details = ProductDetail.objects.filter(product_id=gId).values()
        print(prod_details)

        prod_img = ProductImage.objects.filter(product_id=gId).values("product_img", "product_id", "product_img_id")

        print("Product Images======>", prod_img)  

        size = prod_details[0]["product_size"]
        print(size.split(","))
        
        color = prod_details[0]["product_color"]
        print(color.split(","))

        return render(request, 'productDetails.html', {
            "C_URL": curl,
            "prod_details": prod_details,
            'media_url': media_url,
            'prod_images': prod_img,
            "sizelist": size.split(","),
            "colorlist": color.split(",")
        })

        

