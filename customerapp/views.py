from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import logout
curl = settings.C_URL 
media_url=settings.MEDIA_URL
from ecommerce.models import Customer,ProductDetail,ProductImage,AddToCart,Order
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.contrib import messages
# from ecommerce.models import AddToCart
# from ecommerce.models import Customer
# import json

# Create your views here.
def sessioncheckcustomer_middleware(get_response):
    def middleware(request):
        print("============= request=====:",request.path)
        strpath = request.path
        list1 = strpath.split("/")
        #print("List===>",list1)
        if len(list1)>2:
            
            strnewpath = "/"+list1[1]+"/"+list1[2]+"/"
            print("===========",strnewpath)
            if strnewpath=='C_URL/customerapp/' or strnewpath=='/customerapp/addtocart/' or strnewpath=='/customerapp/editprofile/' or strnewpath == '/customerapp/changepassword/' or strnewpath=='/customerapp/productdetail/'   :
               
                if 'emailid' not in request.session:
                    print("session aaya kya",request.session)   
                    # print("EmailID aaya kya")
                    #          
                    response=redirect('http://localhost:8000/login')
                else:
                    print("kuch bhi")
                    response=get_response(request)
            else:
            
                response=get_response(request)
        else:
            print("else wala part chala")
            return get_response(request)        
        return response   
    return middleware 


def home(request):
    if request.method == "GET":
        #==============session
        email=request.session.get("emailid")
        password =request.session.get("password")
        #==============session  
        qs=Customer.objects.filter(email=email,password=password)
        profile=qs.values()[0]
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
    return render(request,'CustomerHome.html',{'C_URL':curl,'prod_details':prod_details,'prod_images':prod_images,'media_url':media_url,'profile':profile})

def addtocart(request):
    customer_id=request.session.get("customer_id")
    data = AddToCart.objects.filter(customer_id=customer_id).values()
    print("add to cart:==>",data)
    sum=0
    for dic in data:
        print(dic["product_total_price"])
        sum+=dic["product_total_price"]

    return render(request,"AddToCart.html",{"C_URL":curl,'media_url':media_url,'cartdetails':data,'sum':round(sum, 2)})

def increment(request):
    cart_id = request.GET.get('cart_id')
    if cart_id:
        cart_item = AddToCart.objects.get(cart_id=cart_id)
        cart_item.product_quantity += 1
        cart_item.save()

        product_total_price = cart_item.product_quantity * cart_item.product_price
        AddToCart.objects.filter(cart_id=cart_id).update(product_total_price=product_total_price)
        
    return redirect(curl + 'customerapp/addtocart/')


def decrement(request):
    cart_id = request.GET.get('cart_id')
    if cart_id:
        cart_item = AddToCart.objects.get(cart_id=cart_id)
        if cart_item.product_quantity > 1:
            cart_item.product_quantity = cart_item.product_quantity - 1
            cart_item.save()

            product_total_price = cart_item.product_quantity * cart_item.product_price
            AddToCart.objects.filter(cart_id=cart_id).update(product_total_price=product_total_price)
        else:
            cart_item.delete()
    return redirect(curl+'customerapp/addtocart/')


def viewprofile(request):
    if request.method == "GET":
        #==============session
        email=request.session.get("emailid")
        password =request.session.get("password")
        #==============session  
        qs=Customer.objects.filter(email=email,password=password)
        profile=qs.values()[0]
        return render(request,'ViewProfile.html',{'C_URL':curl,'profile':profile})
    

def changepassword(request):
    if request.method == "GET":
        return render(request,'ChangePassword.html',{"C_URL":curl})
    
    elif request.method == "POST":
        oldpassword = request.POST.get('oldpassword')
        newpassword = request.POST.get('newpassword')
        confirmpassword = request.POST.get('confirmpassword')
        print(oldpassword,newpassword,confirmpassword)
        # #==============session
        emailid=request.session.get("emailid")
        # #==============session  
        customer = Customer.objects.filter(email=emailid,password=oldpassword)
        print(customer)
        msg=""
        if customer.exists():
            print("==========Hiii")
            if newpassword==confirmpassword:
              Customer.objects.filter(email=emailid,password=oldpassword).update(password=confirmpassword)
              msg="Customer Password Changed Successfully"  
            else:
              msg="New Password & Confirm Password are mismatch"
        else:
            print("============Hello")
            msg="Please enter correct old password!!"             
                
    return render(request,'ChangePassword.html',{'C_URL':curl,'msg':msg})


def customerdetails(request):
    return render(request,"CustomerDetails.html",{"C_URL":curl})

def editprofile(request):
    if request.method == "GET":
        # ==============session
        email=request.session.get("emailid")
        password =request.session.get("password")
        # ==============session          
        cust = Customer.objects.filter(email=email,password=password).values()
        print(cust[0])
        dropdown_country = ['India', 'Australia']
        selected_country = cust[0]["country"]
        dropdown_state = ['Madhya Pradesh', 'Maharastra']
        selected_state = cust[0]["state"]
        dropdown_city = ['Indore', 'Ujjain', 'Bhopal',"Mumbai","Pune","Nagpur"]
        selected_city = cust[0]["city"]

        return render(request,"EditProfile.html",{"C_URL":curl,"customer":cust[0],"dropdown_city":dropdown_city,"selected_city":selected_city,"dropdown_state":dropdown_state,"selected_state":selected_state,"dropdown_country":dropdown_country,"selected_country":selected_country})
    
    elif request.method=="POST":
        customer_id = request.POST.get('customer_id')
        name = request.POST.get('name')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        print(customer_id,name,mobile,address,city,pincode,country,state)
        Customer.objects.filter(customer_id=customer_id).update(name=name,city=city,pincode=pincode,address=address,mobile=mobile,country=country,state=state)
        msg="Record Updated Successfully"

        return render(request,'Message.html',{'C_URL':curl,'msg':msg})
    elif request.method == "POST":
        customer_id = request.POST.get('customer_id')
        name = request.POST.get('name')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')

        print(customer_id, name, mobile, address, city, pincode, country, state)

        Customer.objects.filter(customer_id=customer_id).update(
            name=name, city=city, pincode=pincode,
            address=address, mobile=mobile,
            country=country, state=state
        )
        msg = "रिकॉर्ड सफलतापूर्वक अपडेट हो गया है।"

        return render(request, 'Message.html', {'C_URL': curl, 'msg': msg})
    

def deleteproduct(request):
    if request.method == "GET":
        cart_id = request.GET.get('id')
        print("Cart Item Id:", cart_id)
        AddToCart.objects.filter(cart_id=cart_id).delete()
        return redirect(curl+'customerapp/addtocart/')


@csrf_exempt
#pip install razorpay
def payment(request):
    #==============session
    email=request.session.get("emailid")
    password=request.session.get("password")
    customer_id=request.session.get("customer_id")
    #==============session  
    listofdic=Customer.objects.filter(email=email,password=password).values()
    print(listofdic[0])

    # authorize razorpay client with API Keys.
    client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    
    # data = { "amount": 500, "currency": "INR", "receipt": "order_rcptid_11" ,"payment_capture":'0'}

    # payment = client.order.create(data=data)
    # print("============== Payment:",payment)

    price=request.GET.get('price')
    
    # # Create a Razorpay Order
    # razorpay_order = client.order.create(data=data)
    # print(razorpay_order)
 
    #return render(request, 'index.html', context=context)
    return render(request,'Payment.html',{'price':price,'customer':listofdic[0],'C_URL':curl,"customer_id":customer_id})

@csrf_exempt
def paymentstatus(request):   
    if request.method=="POST":
    #   #==============session
      customer_id=request.GET.get('id')
      print("customer_id aagai kya?",customer_id)
    #   #==============session  
      addtocart = AddToCart.objects.filter(customer_id=customer_id).values()
      print("===========addtocart:",addtocart)
      print(addtocart[0]["product_brand"])
      product_brand=addtocart[0]["product_brand"]
      product_price=addtocart[0]["product_price"]
      product_size=addtocart[0]["product_size"]
      product_description=addtocart[0]["product_description"]
      product_quantity=addtocart[0]["product_quantity"]
      product_img=addtocart[0]["product_img_name"]
      product_id=addtocart[0]["product_id"]
      customer_id=addtocart[0]["customer_id"]
      product_img_id=addtocart[0]["product_img_id"]
      print(product_brand,product_price,product_size,product_description,product_quantity,product_img,product_id,customer_id,product_img_id)
      #============
    #   cust_details = Customer.objects.get(customer_id=customer_id)
    #   prod_details = ProductDetail.objects.get(product_id=product_id)
    #   prod_img_details = ProductImage.objects.get(product_img_id=product_img_id)
    #   #===============
      #===Order     
      order = Order(product_brand=product_brand,product_price=product_price,product_size=product_size,product_description=product_description,product_quantity=product_quantity,product_image=product_img,customer_id=customer_id,product_id=product_id,product_img_id=product_img_id)
      order.save()

      addtocart = AddToCart.objects.filter(customer_id=customer_id)
      addtocart.delete()
    
    return render(request,'PaymentSuccess.html',{'C_URL':curl})

def Logout(request):
    print("calling logout=============")
    logout(request)
    return redirect('http://localhost:8000/login/')

def productdetail(request):
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

    elif request.method == "POST":
        getquantity = request.POST.get("getquantity")
        print("New Quantity:", getquantity)
        gProductId = request.POST.get("product_id")
        print("Get Product Id:", gProductId)
        gSize = request.POST.get("size")
        gColor = request.POST.get("color")
        print(gSize, gColor)
       
        if  gSize == "Choose an option" or gColor == "Choose an option":           
            messages.success(request, "Please select size and colour.")          
            return redirect(curl + 'customerapp/productdetail/?id=' + gProductId )  
       
        prod_details = ProductDetail.objects.filter(product_id=gProductId).values()
        if not prod_details:
            print("Product Not Found")
            return redirect(curl + 'customerapp/addtocart/')

        p_brand = prod_details[0]["product_brand"]
        p_description = prod_details[0]["product_description"]
        p_price = prod_details[0]["product_sp"]
        p_total_price = float(getquantity) * p_price

        print(p_brand, p_description, p_price, p_total_price)
        print("=======================================")
        try:
            product_image = ProductImage.objects.filter(product_id=gProductId).first()
            if not product_image:
                raise Exception("Product image not found!")

            #==============session 
            customer_id = request.session.get("customer_id")
            #==============session 

            addtocart = AddToCart(
                product_img=product_image,  # ✅ Assign ProductImage instance here
                product_brand=p_brand,
                product_description=p_description,
                product_quantity=getquantity,
                product_size=gSize,
                product_color=gColor,
                product_price=p_price,
                product_total_price=p_total_price,
                customer_id=customer_id,
                product_id=gProductId,
            
            )
            addtocart.save()
            msg = "Product Added to Cart"

        except Exception as e:
            print("Exception Occur:", e)
            msg = "Product Not Added to Cart!"

        return redirect(curl + 'customerapp/addtocart/')

