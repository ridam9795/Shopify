from django.shortcuts import render, redirect
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from PayTm import Checksum
import json
from django.core.serializers import serialize
from django.http import JsonResponse


MERCHANT_KEY = 'kbzk1DsbJiV_O3p5'


def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    product_data = list(Product.objects.values())
    
    params = {'allProds': allProds, 'Products': Product.objects.all(),
              'product_data': product_data}
    # print(Product.objects.all())
    return render(request, 'shop/index.html', params)


def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower() or query in item.subcategory.lower():
        return True
    return False


def search(request):
    query = request.GET.get("search")
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if n != 0:
            allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds, 'Products': Product.objects.all(),
              'msg': ""}
    # print(Product.objects.all())
    if len(allProds) == 0 or len(query) < 3:
        params = {'msg': 'Please make sure to enter relevant search query'}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
        return render(request, 'shop/contact.html', {'thank': thank})
    return render(request, 'shop/contact.html')


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        print(orderId, email)
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append(
                        {'text': item.update_desc, 'time': item.timestamp.strftime("%d %B , %Y")})
                    response = json.dumps(
                        {"status": "success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)

            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)

    return render(request, 'shop/prodView.html', {'product': product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        amount = request.POST.get('amount', '')
        address = request.POST.get('address1', '') + \
            " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Order(items_json=items_json, name=name, email=email, address=address, city=city,
                      state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id,
                             update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        # request paytm to transfer the amount to your account after payment by user
        param_dict = {
            'MID': 'WorldP64425807474247',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(order.amount),
            'CUST_ID': 'email',
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(
            param_dict, MERCHANT_KEY)

        return render(request, 'shop/paytm.html', {'param_dict': param_dict, 'user': request.user})
    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    checksum = 'sds'
    print("form", form)
    status = ""
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'STATUS':
            status = form[i]

        if i == 'CHECKSUMHASH':
            checksum = form[i]

    print("status: ", status)
    verify = False
    try:
        verify = Checksum.verify_checksum(
            response_dict, MERCHANT_KEY, checksum)
    except:
        print("Exception occured")

    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' +
                  response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
    # paytm will send you post request here.


def handlelogin(request):
    if request.method == "POST":
        loginUserName = request.POST.get("loginUserName")
        loginPassword = request.POST.get("loginPassword")
        user = authenticate(username=loginUserName, password=loginPassword)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
        else:
            messages.error(request, "invalid credentials")

    return redirect('/')


def handlesignup(request):
    if request.method == "POST":
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        username = request.POST.get("username")
        signUpEmail = request.POST.get("signUpEmail")
        signUpPassword = request.POST.get("signUpPassword")
        print(firstName, lastName, username, signUpEmail, signUpPassword)
        myuser = User.objects.create_user(
            username, signUpEmail, signUpPassword)
        myuser.first_name = firstName
        myuser.last_name = lastName
        myuser.save()

    return redirect('/')


def handlelogout(request):
    print(request)
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("/shop")

def viewCart(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    product_data = list(Product.objects.values())
    
    params = {'allProds': allProds, 'Products': Product.objects.all(),
              'product_data': product_data}
    # print(Product.objects.all())
    return render(request, 'shop/viewcart.html', params)