from flask import Blueprint, flash, redirect, render_template, request,session, url_for
from . import conn
import uuid
import datetime
from uuid import uuid4
# from inventory import inventoryfun

views = Blueprint('views',__name__)
db = conn.connection()

@views.route('/')
def home():
    print("Inside View.Home")
    documents = db.products.find()
    products = [{item: data[item] for item in data if item != '_id'} for data in documents]
    return render_template("home.html",products=products)


@views.route('/add',methods=["GET", "POST"])
def addToCart():
    print("Inside View.Add to cart")
    if(session['name']):
        temp=request.args
        temp=temp.to_dict(flat=False)
        pid=temp["pid"][0]
        qty=temp["qty"][0]
        if (pid in session["cart"]):
            idx = session["cart"].index(pid)
            session["qty"][idx]=str(int(qty)+int(session["qty"][idx]))  
            print("qNew Quantity si ",session["qty"])
            documents = db.products.find()
            products = [{item: data[item] for item in data if item != '_id'} for data in documents]
            return render_template("home.html",products=products)
        qty=temp["qty"][0]
        product = db.products.find_one({'item_id':int(pid)})
        if product['Quantity']<int(qty):
            flash('Item Out of Stock',category='error')
            documents = db.products.find()
            products = [{item: data[item] for item in data if item != '_id'} for data in documents]
            return render_template("home.html",products=products)
        else:
            session["cart"].append(pid)
            session["qty"].append(qty)
      
        documents = db.products.find()
        products = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return render_template("home.html",products=products)

@views.route('/remove')
def remove():
    print("Inside View.remove to cart")
    if(session['name']):
        temp=request.args
        temp=temp.to_dict(flat=False)
  
        item_id=temp["itemid"][0]

        idx=session["cart"].index(item_id)
        session["cart"].pop(idx)
        session["qty"].pop(idx)

    return redirect(url_for('views.viewCart'))

@views.route('/payment')
def payment():
    print("Inside Payment Function ")
    order_id=uuid.uuid4()
    payment_id=uuid.uuid4()
    email_id = session["name"]
    status=True
    payment_type=request.form.get('cardtype')
    session['paymentType']=payment_type
    shipping_address={}
    #shipping Address
    if payment_type== "cash":
        status=False
    if status==True:
        user = db.customers.find_one({"email":email_id})
        shipping_address=user['shipping_address']
        # print("----------------",shipping_address['Street1'])
        payment_details=user['payment_details']
        # order Table details 
        print(order_id,payment_id,email_id,payment_type,shipping_address['country'])
        # flash('Login Successfull!!',category='success')
        return render_template("payment.html",shippingAddress=shipping_address,paymentDetails=payment_details,status=status)
    else:
        user = db.customers.find_one({"email":email_id})
        shipping_address=user['shipping_address']
        payment_details=user['payment_details']
        time = datetime.datetime.now()
        return render_template("payment.html",shippingAddress=shipping_address,paymentDetails=payment_details,status=status)


@views.route('/updatepayment')
def paymentdone():
    order_id=str(uuid.uuid4())
    payment_id=str(uuid.uuid4())
    email_id = session["name"]
    status=True
    payment_type=session['paymentType']
    session['paymentType']=None
    payment_type="credit"
    shipping_address={}
    if payment_type== "Cash":
        status=True
    if status==True:
        user = db.customers.find_one({"email":email_id})
        shipping_address=user['shipping_address']
        payment_details=user['payment_details']
        time = datetime.datetime.now()
        products=[]
        cartslist=session["cart"]
        qtylist=session["qty"]
        finalprice=0
        item_details=[]
        for i in range(len(cartslist)):
            print("index of ..",)
            data = db.products.find_one({'item_id':int(cartslist[i])})
            dbquantity = int(data['Quantity'])-int(qtylist[i])
            db.products.update_one({'item_id':int(cartslist[i])}, { "$set": { "Quantity": int(dbquantity) } } )
            temp=round(float(data['price'])*int(qtylist[i]),2)
            finalprice+=temp
            products.append({'item_id':data['item_id'],'title':data['title'],'price':float(data['price']),'qty':int(qtylist[i]),'subtotalprice':temp})
            individual_item={
                "item_id": data['item_id'],
                "qty": int(qtylist[i]),
                "discount": 0.0,
                "price": float(data['price']),
                "category": data['category']
            }
            item_details.append(individual_item)
        tax= round(finalprice*0.09,2)
        total_price_tax=round(finalprice+tax,2)
        payment_status = "successfull"
        input_data =  {
            "order_id": order_id,
            "payment_id": payment_id,
            "email_id": email_id,
            "payment_type": payment_type,
            "shippingAddress": shipping_address,
            "payment_details": payment_details,
            "time_payment": time,
            "total_price_tax": total_price_tax,
            "payment_status": payment_status
            }
        db.payment.insert_one(input_data)
        data = {
        "order_id": order_id,
        "item_details": item_details,
        "email_id": email_id,
        "total_price": total_price_tax,
        "order_status": "Delivered",
        "time_order": time
        }
        db.orders.insert_one(data)
        session["cart"]=[]
        session["qty"]=[]
        session["paymentType"]=None
        flash(' Order Placed!!',category='success')
        return redirect(url_for('views.home'))
    return render_template("payment.html")

@views.route('/cart')
def viewCart():
    print("Inside View.viewCart")
    products=[]
    cartslist=session["cart"]
    qtylist=session["qty"]
    finalprice=0
    for i in range(len(cartslist)):
        print("index of ..",)
        data = db.products.find_one({'item_id':int(cartslist[i])})
        temp=round(float(data['price'])*int(qtylist[i]),2)
        finalprice+=temp
        products.append({'item_id':data['item_id'],'title':data['title'],'price':float(data['price']),'qty':int(qtylist[i]),'subtotalprice':temp})
    tax= round(finalprice*0.09,2)
    pricewithtax=round(finalprice+tax,2)
    return render_template("cart.html",data=products,finalprice=round(finalprice,2),tax=tax,pricewithtax=pricewithtax)


@views.route('/orders')
def Orders():

    print("Inside myorder page ")
    documents = db.orders.find({'email_id':session["name"]})
    orders = [{item: data[item] for item in data if item != '_id'} for data in documents]
    print(orders)

    return render_template("orders.html",data=orders)

@views.route('/viewOrders',methods=["GET", "POST"])
def viewOrders():
    print("Inside viewOrders page ")
    temp=request.args
    temp=temp.to_dict(flat=False)
    orderid=temp["orderid"][0]
    singleorder = db.orders.find_one({'order_id':orderid})
    orderid=singleorder['order_id'] 
    temp={}
    orderdata=[]
    for item in singleorder['item_details']:
        print(item['item_id'])
        product = db.products.find_one({'item_id':item['item_id']})
        title = product['title']
        category= item['category']
        returnid = str(singleorder['order_id'])+","+str(item['item_id'])
        price=item['price']
        quantity=item['qty']
        temp={
        "orderid":singleorder['order_id'],
        "emailid": singleorder['email_id'],
        "totalprice":singleorder['total_price'],
        "status":singleorder['order_status']
        }   
        temp["title"]=title
        temp["category"]=category
        temp["returnid"]=returnid
        temp["price"]=price
        temp["quantity"]=quantity
        print("Before Adding ....")
        print(temp)
        orderdata.append(temp)
        temp={}
    return render_template("viewOrder.html",data=orderdata)

@views.route('/returns',methods=["GET", "POST"])
def returns():
    print("Inside Returns Function")
    temp=request.args
    temp=temp.to_dict(flat=False)
    returnid=temp["returnid"][0]
    li=returnid.split(',')
    orderid= li[0]
    itemid=li[1]
    item= db.orders.find_one({'order_id':orderid})
    ordered_time = item["time_order"]
    items= item["item_details"]
    temp={}
    for i in items: 
        print(i['item_id'])
        if str(i['item_id'])==str(itemid):
            temp['qty']=i['qty']
            temp['discount']=i['discount']
            temp['price']=i['price']
            temp['category']=i['category']
    if(temp["category"] in ["vegetables","diary"]):
        current_time = datetime.datetime.now()
        duration = current_time - ordered_time
        duration_in_s = duration.total_seconds()  
        days  = duration.days                         # Build-in datetime function
        days  = divmod(duration_in_s, 86400)[0] 
        if (days>=1):
            flash(' This Item Cannot be returned',category='error')
            return redirect(url_for('views.Orders'))      
    current_time = datetime.datetime.now()
    product = db.products.find_one({'item_id':int(itemid)})
    title = product['title']
    data={ "return_id":returnid,
        "order_id":orderid,
        "item_id":itemid,
        "item_qty":temp['qty'],
        "price":temp['price'],
        "category":temp["category"],
        "email_id":session["name"],
        "time_stamp":current_time,
        "title":title,
        "eligibility":True,
        "return_status":"return initiated"
    }
    db.returns.insert_one(data)
    flash(' Order Returned initiated',category='success')    
    return redirect(url_for('views.home'))


@views.route('/adminaccept',methods=["GET", "POST"])
def adminaccept():
    print("Inside admin order accept page ")
    temp=request.args
    print(request.args)
    temp=temp.to_dict(flat=False)
    print(temp)
    returnid=temp["returnid"][0]

    db.returns.update_one({"return_id" : returnid},{"$set":{"return_status":"Accepted"}})

    itemid = returnid.split(',')[1]
    print("Item_id is ",itemid)
    # product = db.products.find_one({'item_id':int(pid)})
    product=db.products.find_one({'item_id':int(itemid)})
    print(product)
    dbquantity = product['Quantity']
    print("Products Quantity is ",dbquantity)
    return_order_details = db.returns.find_one({'return_id':returnid})
    return_quantity=return_order_details['item_qty']
    new_quantity = dbquantity + return_quantity

    db.products.update_one({'item_id':int(itemid)}, { "$set": { "Quantity": int(new_quantity) } } )
  
    return  redirect(url_for('views.allreturns'))

@views.route('/adminreject',methods=["GET", "POST"])
def adminreject():
    print("Inside admin order reject page ")
    temp=request.args
    print(request.args)
    temp=temp.to_dict(flat=False)
    print(temp)
    returnid=temp["returnid"][0]
    db.returns.update_one({"return_id" : returnid},{"$set":{"return_status":"Rejected"}})
    return  redirect(url_for('views.allreturns'))


@views.route('/myreturns',methods=["GET", "POST"])
def myreturns():
    print("Inside my returns page ")
    return_orders=db.returns.find({'email_id':session['name']})
    orders = [{item: data[item] for item in data if item != '_id'} for data in return_orders]
    return render_template("myreturns.html",orders=orders)



@views.route('/allreturns',methods=["GET", "POST"])
def allreturns():
    print("Inside Admin returns page ")
    return_orders=db.returns.find({'return_status':"return initiated"})
    orders = [{item: data[item] for item in data if item != '_id' } for data in return_orders]
    return render_template("adminreturns.html",orders=orders)


@views.route('/inventory',methods=["GET", "POST"])
def allinventory():
    print("Inside Admin inventory page ")
    documents = db.products.find()
    products = [{item: data[item] for item in data if item != '_id'} for data in documents]
    # orders=inventoryfun()
    return render_template("inventory.html",data=products)


@views.route('/inventoryupdate',methods=["GET", "POST"])
def inventoryupdate():
    
    if(request.method=="POST"):
        print("Inside Update Inventory method")
        db.products.update_one({
            "item_id" :int(request.form.get('itemid'))},
            {"$set":{
                "Quantity":int(request.form.get('qty')),
                "title":request.form.get('title'),
                "Description":request.form.get('desc'),
                "price":request.form.get('price'),
                "category":request.form.get('category')
                }
            })
        flash(' Item Details Updated!!',category='success')
        return redirect(url_for('views.allinventory'))
    return render_template("/inventory.html")

@views.route('/addinventory',methods=["GET", "POST"])
def addinventory():
    print("Inside Add inventory page")
    if (request.method == "POST"):
        # item_id=uuid.uuid4().int & (1<<64)-1
        data={
        "item_id": int(request.form.get('itemid')),
        "title": request.form.get('title'),
        "Description": request.form.get('desc'),
        "price": request.form.get('price'),
        "category": request.form.get('category'),
        "discount": 0,
        "sku": {},
        "Quantity": int(request.form.get('qty'))
        }
        print(data)
        db.products.insert_one(data)
        flash(' New product Added!!!',category='success')


    return render_template("/addinventory.html")

@views.route('/allorders')
def allOrders():

    print("Inside myorder page ")
    documents = db.orders.find()
    orders = [{item: data[item] for item in data if item != '_id'} for data in documents]
    print(orders)
    # print("Inside View.Home")
    # documents = db.products.find()
    # products = [{item: data[item] for item in data if item != '_id'} for data in documents]
    # for i in products:
    #     print(i)


    # time , order status , tracking id ,Sno
    # return render_template("home.html",products=products)
    return render_template("allorders.html",data=orders)


@views.route('/allCustomer')
def allCustomer():

    print("Inside allCustomer")
    documents = db.customers.find()
    customers = [{item: data[item] for item in data if item != '_id'} for data in documents]
    print(customers)
    # print("Inside View.Home")
    # documents = db.products.find()
    # products = [{item: data[item] for item in data if item != '_id'} for data in documents]
    # for i in products:
    #     print(i)


    # time , order status , tracking id ,Sno
    # return render_template("home.html",products=products)
    return render_template("allcustomer.html",data=customers)
