from pkg import app
import json
from datetime import datetime
import requests,random,secrets
from flask import request,render_template,redirect,flash,session,url_for
from markupsafe import escape
from flask_wtf.csrf import CSRFError
from pkg.models import db,Customer,Product,Payment
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps




def MagerDicts(dict1,dict2):
    if isinstance(dict1,list) and isinstance(dict2,list):
        return dict1 + dict2
    elif isinstance(dict1,dict) and isinstance(dict2,dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False



def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('cust_online') != None:
            return f(*args,**kwargs)
        else:
            flash('You must be logged in to access this page', category='error')
            return redirect('/login/')
    return check_login


@app.route('/landing/')
def landing():
    products = db.session.query(Product).all()
    
    
    return render_template('index2.html',title='Home|login',products=products)


@app.route('/')
def home():
   
        products = db.session.query(Product).all()
        
        return render_template('index.html',title='Home', products=products)



@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else: #retrieve
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        pwd2 = request.form.get('pwd2')

        if pwd != pwd2:
            flash('Passwords do not match', category='error')
            return redirect('/register/')
        
        hashed = generate_password_hash(pwd)
        # hashed = generate_password_hash(pwd2)

        customer=db.session.query(Customer).filter(Customer.cust_email==email).first()
        
        if customer:
            flash('Email already exist',category='error')
            return redirect('/register/')
        else:
        #insert
            cust_deets = Customer(cust_fname=fname,cust_lname=lname,cust_email=email,cust_password=hashed)

        #add to db
            db.session.add(cust_deets)
            db.session.commit()
            userid = cust_deets.cust_id
            session['cust_online'] = userid
            return redirect('/login/')
    
        # return render_template('register.html',title='Home|Sign Up')

def get_user_by_id(id):
    deets = db.session.query(Customer).get(id)
    return deets


#change to foodstuff...
@app.route('/shops/')
def shops():
    return render_template('shops.html',title='Home|Shops')


@app.route('/profile/',methods=['POST','GET'])
@login_required
def profile():
    id = session.get('cust_online')
    userdeets = db.session.query(Customer).get(id) 


    if request.method=='GET':
        return render_template('profile.html',userdeets=userdeets)
    else: #retrieve
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        phone=request.form.get('phone')
        address=request.form.get('address')
        #update
        deets = db.session.query(Customer).get(id) #Customer.query.get(id)
        deets.cust_fname=fname
        deets.cust_lname=lname
        deets.cust_phone=phone
        deets.cust_address=address
        
        db.session.commit()
        return redirect(url_for('dash'))


@app.route('/category/')
def category():
    products=db.session.query(Product).all()
    return render_template('category.html',title='Home|login',products=products )

@app.route('/products/')
def product():
    products=db.session.query(Product).all()
    return render_template('products.html',title='Home|Products',products=products)

@app.route('/login/',methods=['GET','POST'])
def login(): 
    if request.method == 'GET':
         return render_template('login.html')
    else:
        email=request.form.get('email')
        password = request.form.get('pwd')
        if email == '' or password == '':
            flash('Both fields must be supplied',category='error')
            return redirect('/login/')
        else:
            customer=db.session.query(Customer).filter(Customer.cust_email==email).first()
            if customer != None:
                stored_hash = customer.cust_password #get hashed password from database
                chk = check_password_hash(stored_hash,password)
                if chk == True: #login was successfull
                    flash('Logged in successfully!',category='success')
                    session['cust_online'] = customer.cust_id
                    return redirect('/dashboard/')
                else:
                    flash('Invalid password',category='error')
            else:
                flash('Invalid username',category='error')
            return redirect('/login/')
            
       

@app.route('/dashboard/')
@login_required
def dash():
    id = session.get('cust_online')

    customer = get_user_by_id(id) #this customer is an obj of the customer table
    
    
    return render_template('dashboard.html',customer=customer,title='Home|Dashboard')
  
       


@app.route('/about/')
def about():
    return render_template('about.html',title='Home|About')

@app.route('/logout/')
def logout():
    if session.get('cust_online') and session.get('Shoppingcart'):
       session.pop('cust_online')
       session.pop('Shoppingcart')
    return redirect('/login/')
       
@app.route('/details/<int:id>')
def details(id):
    products = db.session.query(Product).filter(Product.prod_id==id)

    return render_template('details.html',title='details', products=products)

#.................add to cart........(Merger at the Top)............
       
@app.route('/addcart/',methods=['POST'])
def addcart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        product = Product.query.filter_by(prod_id=product_id).first()
        if product_id and quantity and request.method=='POST':
            DictItems = {product_id:{'name':product.prod_title,'price':product.prod_price,'quantity':quantity,'image':product.prod_image}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    print("This product is already in you cart")
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'],DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
        
       
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)

#cart is for the display....
@app.route('/cart/',methods=['POST','GET'])
def cart():
        if 'Shoppingcart' not in session or len(session['Shoppingcart'])==0:
            return redirect(url_for('landing'))
        Subtotal = 0
        grandtotal = 0
    

        for key, product in session['Shoppingcart'].items():
            Subtotal += float(product['price']) * int(product['quantity'])
           
            grandtotal = float("%.2f" % Subtotal)
            session['Shoppingcart']
            session['total']=grandtotal
            

        return render_template('cart.html',grandtotal=grandtotal,Subtotal=Subtotal)

@app.route('/delete_item/<int:id>')
def delete_item(id):
    if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key)==id:
                session['Shoppingcart'].pop(key,None)
                return redirect(url_for('cart'))
    except Exception as e:
        print(e)
        return redirect(url_for('cart'))

#.................add to cart....................



@app.route('/foodstuff/')
def foodstuff():
    products= db.session.query(Product).all()
    return render_template('index_include.html',products=products)

@app.route('/dp/')
def dp():
    
    return render_template('change_dp.html')

    # return render_template('cart.html',title='Cart', products=products)




#-------------CHANGE DP START----------------------------------
@app.route('/changedp/',methods=['POST','GET'])
@login_required
def change_dp():
    id = session.get('cust_online')
    # user_id = get_user_by_id(id)
    user=db.session.query(Customer).filter(Customer.cust_id==id).first()


    
    if request.method=='POST':
        dp=request.files.get('dp')
        
        filename=dp.filename #getting the img name
        allowed=['jpg','png','jpeg','JPG','PNG','JPEG']
        dp_deets=filename.split('.')
        ext=dp_deets[-1]

        if filename:
            if ext in allowed:
                newname = secrets.token_hex(10)+ '.' +ext
                dp.save('pkg/static/products/' + newname )

                user.cust_pix=newname
                db.session.commit()
                flash('profile picture uploaded successfully!',category='success')
                return redirect('/dashboard/')
            else:
                flash('file extension not allowed,allowed extension(jpg,png,jpeg)',category="error") 
                return redirect('/profile/')
        else:
            flash('You need to select a file for upload and provide title',category='warn')
            return redirect('/profile/')
        

    return redirect('/dashboard/')


#-------------CHANGE DP END----------------------------------

#.............PAYMENT START.....................


#.............LANDING START.....................


@app.route("/pay/landing/")
def payment_landing_page():
    ref=session.get("pay_ref") #the one we know about
    paystackref=request.args.get("reference") #the one coming from paystack
    if ref == paystackref:
        url="https://api.paystack.co/transaction/verify/" + ref
        headers={"Content-Type":"application/json", "Authorization": "Bearer sk_test_f4ad1a37b74d6df89e8e57f221b78304916adf92"}
        response= requests.get(url,headers=headers)#connecting to paystack
        response_json=response.json()
        #update database
        pay =Payment.query.filter(Payment.payment_ref==ref).first()
        if response_json['status']==True:
            ip = response_json["data"]["ip_address"]
            pay.payment_status="paid"
            pay.payment_date=datetime.now()
        else:
            pay.payment_status="failed"
        db.session.commit()
        return redirect(url_for('landing'))
    else:
        flash("Invalid Parameter detected",category="error")
        return redirect("/reports/")



#.............LANDING ENDS.....................



@app.route('/checkout/', methods=['POST', 'GET'])
def checkout():
    id = session.get('cust_online')
    user_id = get_user_by_id(id)
    ref = "AF_" + str(random.randint(100, 500000) + 100000)
    session['pay_ref'] = ref
    total = session.get('total')
    push = Payment(amount_paid=total, payment_ref=ref, payment_status='pending', transaction_details='--',payment_custid=user_id.cust_id)
    db.session.add(push)
    db.session.commit()
    return redirect('/payconfirm/')




@app.route('/paystack/initialize/',methods=['POST','GET'])
def paystack_initialize():
    ref = session.get('pay_ref')
    if ref != None:
        
        paydeets = Payment.query.filter(Payment.payment_ref == ref).first()
        amount = paydeets.amount_paid * 100
        email = paydeets.payment_cust.cust_email
        callback_url = "http://127.0.0.1:5000/pay/landing/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk_test_f4ad1a37b74d6df89e8e57f221b78304916adf92"
        }
        url = "https://api.paystack.co/transaction/initialize"
        data = {"amount": amount,"email":email, "reference": ref, "callback_url": callback_url}
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_json = response.json()
            if response_json and response_json["status"]==True:
                checkoutpage = response_json["data"]["authorization_url"]
                return redirect(checkoutpage)
            else:
                flash(f'Paystack returned an error: {response_json["message"]}', category="error")
                return redirect('/checkout/')
        except:
                flash("We could not connect to paystack", category="error")
                return redirect("/checkout/")

    else:
        flash('please complete the Form', category = "error")
        return redirect('/checkout/')
    
#................................................................................................................................


@app.route("/payconfirm/", methods=['POST', 'GET'])
def payconfirm():
    """Route fetches details of the donation form submitted by the user so they can confirm if they want to go ahead to edit"""
    ref = session.get("pay_ref")
    if ref != None:
        payment_deets=Payment.query.filter(Payment.payment_ref==ref).first()
         # Clear the shopping cart session after payment is confirmed
        session.pop('Shoppingcart', None)
        
        return render_template("confirm.html", payment_deets=payment_deets)
    else:
        flash("Please complete the payment form", category="error")
        return redirect("/checkout/")
#.............PAYMENT END.....................




#error section starts

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html',error=error),404




@app.errorhandler(400)
def page_not_found(error):
    return render_template('error400.html',error=error),400






#error section ends

@app.route('/clearses/')
def clearses():
    session.clear()
    return 'thanks'