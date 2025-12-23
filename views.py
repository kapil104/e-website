from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
from .helpers import send_forget_mail
from ecommerce.models import Customer,ProductDetail,ProductImage,AddToCart
media_url=settings.MEDIA_URL
curl = settings.C_URL 
import uuid
from django.db.models import Q
# import json
from django.template.loader import render_to_string

# from customerapp import views

def index(request):
    query = request.GET.get('q','')
    print("Query:",query)
    results = ProductDetail.objects.filter(product_brand__icontains=query).values() if query else ProductDetail.objects.all().values()
    prod_img = ProductImage.objects.all().values("product_img","product_id")
        # print(prod_img)
    prod_images=[] 
    for dic in results:
        for imgdic in prod_img:
            if dic["product_id"] == imgdic["product_id"]:
                prod_images.append(imgdic)
                break
    #print(prod_images)
    print(results,"===========")
    return render(request, 'Index.html', {'prod_details': results, 'query': query,'prod_images':prod_images,'media_url':media_url})

def productdetails(request):
    if request.method == "GET":
        gId = request.GET.get('id')
        print("Get Product Image:",gId)
        #=======
        prod_details=ProductDetail.objects.filter(product_id=gId).values()
        print(prod_details)
        prod_img = ProductImage.objects.filter(product_id=gId).values("product_img","product_id")
        print(prod_img)
        
        print("Product Images======>",prod_img)  
        size=prod_details[0]["product_size"]
        print(size.split(","))
        color=prod_details[0]["product_color"]
        print(color.split(","))
        
        return render(request,'ProductDetails.html',{"C_URL":curl,"prod_details":prod_details,'media_url':media_url,'prod_images':prod_img,"sizelist":size.split(","),"colorlist":color.split(",")})
    
    elif request.method == "POST":
        getquantity = request.POST.get("getquantity")
        print("New Quantity:",getquantity)
        gProductId = request.POST.get("product_id")
        print("Get Product Id:",gProductId)
        gSize = request.POST.get("size")
        gColor = request.POST.get("color")
        print(gSize,gColor)

        prod_details=ProductDetail.objects.filter(product_id=gProductId).values()
        # print(prod_details)

       
        p_brand=prod_details[0]["product_brand"]
        p_description=prod_details[0]["product_description"]
        p_price=prod_details[0]["product_sp"]
        p_total_price=float(getquantity)*p_price
        print(p_brand,p_description,p_price,p_total_price)
        print("=======================================")

        prod_img = ProductImage.objects.filter(product_id=gProductId).values()
        # print(prod_img)
        p_img_id = prod_img[0]["product_img_id"]
        p_img_name = prod_img[0]["product_img"]
        print(p_img_id,p_img_name)

        return redirect(curl+'login')    
    
def product_list(request):
    if request.method == "GET":
        prod_details=ProductDetail.objects.all().values()
        print(prod_details)
        prod_img = ProductImage.objects.all().values("product_img","product_id")
        # print(prod_img)
        prod_images=[] 
        for dic in prod_details:
            for imgdic in prod_img:
                if dic["product_id"] == imgdic["product_id"]:
                    prod_images.append(imgdic)
                    break
        # print(prod_images)  
        return render(request,'Index.html',{'C_URL':curl,'prod_details':prod_details,'prod_images':prod_images,'media_url':media_url}) 

def search_products(request):
    query = request.GET.get('q', '')
    results = ProductDetail.objects.filter(product_brand__icontains=query).values() if query else ProductDetail.objects.all().values()
    prod_img = ProductImage.objects.all().values("product_img","product_id")
        # print(prod_img)
    prod_images=[] 
    for dic in results:
        for imgdic in prod_img:
            if dic["product_id"] == imgdic["product_id"]:
                prod_images.append(imgdic)
                break
    return render(request, 'SearchResult.html', {'prod_details': results, 'query': query,'prod_images':prod_images,'media_url':media_url})
       


def contact(request):
    # return HttpResponse("<h1>welcome to the contact</h1>")
    return render (request, 'contact.html',{"C_URL":curl})

# def home(request):
#     # return HttpResponse("<h1>welcome to the home</h1>")
#     return render (request, 'home.html')

def about(request):
    # return HttpResponse("<h1>welcome to the about</h1>")
    return render (request, 'about.html',{"C_URL":curl})

# def help(request):
#     # return HttpResponse("<h1>welcome to the help</h1>")
#     return render (request, 'help.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login(request):
    if request.method == "GET":
        return render(request,'Login.html',{"C_URL":curl})
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            qsobj = Customer.objects.filter(email=email,password=password)
            print(qsobj.values())
            role=qsobj.values()[0]["role"]
            print(role)
            status=qsobj.values()[0]["status"]
            print(status)
            #for session ============================
            '''
            Session data can be accessed and modified using the request.session attribute in views. This attribute behaves like a dictionary, allowing you to store and retrieve values associated with the current session. Session data persists until it expires or is explicitly deleted.
            Django sessions enable storing and retrieving data associated with specific website visitors across multiple requests. This mechanism addresses the stateless nature of HTTP, allowing applications to maintain user-specific information, such as login status or shopping cart contents. Django handles session management by using a session ID stored in a cookie on the client's browser and the corresponding session data stored server-side.
            '''
            request.session["emailid"]=qsobj.values()[0]["email"]
            request.session["password"]=qsobj.values()[0]["password"]
            request.session["role"]=qsobj.values()[0]["role"]
            request.session["customer_id"]=qsobj.values()[0]["customer_id"]
            # print("cid",customer_id)
            #for session ============================

            if status == 1:
                if role=="admin":
                  print("admin")
                  return redirect(curl+'adminapp/')
                elif role=="customer":
                  print("customer")
                  return redirect(curl+'customerapp/')
            else:
                msg="Please contact admin to verify customer"    
                return render(request,"Login.html",{"C_URL":curl,"msg":msg})
        except Exception as obj:
            return render(request,"Login.html",{"C_URL":curl,"msg":"Please enter correct email or password"})
        
def forgotPassword(request):
    if request.method == "GET":
        return render(request,'forgotPassword.html',{"C_URL":curl})
    
    if request.method == 'POST':
        email=request.POST.get('email')
        data = Customer.objects.filter(email=email).first()
        # print("Customer Record:",data)
        # print("Data Type is:",type(data))
        print("===============================")
        if not data:
            print("No User Found with this email")
            msg ="No User Found with this email"
            return redirect(curl+'login/')
            
        cust_obj = Customer.objects.filter(email=email).first()

        print(type(cust_obj),cust_obj.email)
        #=====Generate a random UUID.
        token = str(uuid.uuid4())
        #===== Save token ====#
        cust = Customer.objects.get(email=cust_obj.email)
        cust.forgot_password_token = token
        cust.save()
        #=========Save token =====#
        send_forget_mail(cust_obj.email,token)
        print("Email is send to your gmail id")
        return render(request,'forgotPassword.html',{"C_URL":curl})
    return render(request,'forgotPassword.html',{"C_URL":curl,"customer_id":cust_obj.customer_id})

def resetpassword(request,token):
    cust_obj=Customer.objects.filter(forgot_password_token=token).first()
    print(cust_obj.customer_id)

    if request.method == 'POST':
        newpassword=request.POST.get('newpassword')
        confirmpassword=request.POST.get('confirmpassword')
        c_id=request.POST.get('customer_id')

        if c_id is None:
           print("No User Id Found")
           return redirect(curl+'login/')
       
        if newpassword != confirmpassword:
           print("newpassword and confirmpassword is not same")
           return redirect(curl+'resetpassword/'+token)
        
        Customer.objects.filter(customer_id=c_id).update(password=confirmpassword)
        
        print("Password Reset Successfully")
        return render(request,'Login.html',{"C_URL":curl,"msg":"Password Reset Successfully"})
    
    elif request.method == "GET":
        return render(request,'ResetPassword.html',{"C_URL":curl,"customer_id":cust_obj.customer_id})

def register(request):
    if request.method == "GET":
        return render(request,'register.html',{"C_URL":curl})
    if request.method == "POST":
        name1 = request.POST.get("name")
        email1 = request.POST.get("email")
        password1 = request.POST.get("password")
        mobile1 = request.POST.get("mobile")
        country1 = request.POST.get("country")
        state1 = request.POST.get("state")
        city1 = request.POST.get("city")
        address1 = request.POST.get("address")
        pincode1 = request.POST.get("pincode")
        print("Name:",name1)
        print("Email:",email1)
        print("Password:",password1)
        print("Mobile:",mobile1)
        print("Country:",country1)
        print("State:",state1)
        print("City:",city1)
        print("Address:",address1)
        print("Pincode:",pincode1)
        customer=Customer(name=name1,password=password1,email=email1,mobile=mobile1,address=address1,city=city1,pincode=pincode1,country=country1,state=state1)
        msg=""
        try:
            customer.save()
            msg="Customer Register Successfully!!"
        except Exception as obj:
            print("Exception:",obj)
            msg="Customer Not Register, Please try Again"       
        return render(request,"register.html",{"C_URL":curl,"msg":msg})

    






