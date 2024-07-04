import secrets,os
from pkg import app
from flask import request,render_template,redirect,flash,session,url_for
from markupsafe import escape
from flask_wtf.csrf import CSRFError
from pkg.models import db,Customer,Admin,Product,Category
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps



def get_admin_by_id(id): #bcs of thesession protection in other routes,whenever i need access,it should be done with getting their id
    deets = db.session.query(Admin).get(id)
    return deets


def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('adminonline') != None:
            return f(*args,**kwargs)
        else:
            flash('You must be logged in to access this page', category='error')
            return redirect('/adminlogin/')
    return check_login

@app.route('/admin/',methods=['POST','GET'])
# @login_required
def admin():
    # if request.method=="POST":
    if session.get('adminonline') != None:
        categories=Category.query.all()
        products=Product.query.all()
        return render_template('admindash.html',products=products,categories=categories)
    else:
        flash('You need to login to access this page',category='info')
        return redirect('/adminlogin/')

@app.route('/adminlogin/',methods=['GET','POST'])
def admin_login():
    if request.method=='GET':
        return render_template('adminlogin.html')
    else:
        email=request.form.get('email')
        password=request.form.get('pwd')
        if email == "" and password == "":
            flash("both field must be supplied",category="error")
            return redirect('/admin/')
        else:
            admin=db.session.query(Admin).filter(Admin.admin_email==email).first()
            if admin != None: #username from the form matched with the username in the db
                stored_password = admin.admin_pwd
                chk = check_password_hash(stored_password,password)
                if chk:
                    session['adminonline'] = admin.admin_id
                    flash('You are Successfully logged In.',category='success')

                    return redirect(url_for('admin'))
                else:
                    flash('Invalid password',category='error')
            else:
                flash('Invalid Admin Email',category='error')
        return redirect(url_for('admin_login'))

    # return render_template('adminlogin.html',email=email,password=password,title='Login|Admin')



    
@app.route('/addpost/',methods=['GET','POST'])
@login_required
def addpost():
   
    if request.method=='POST':
        title=request.form.get('title')
        content=request.form.get('content')
        price = request.form.get('price')
        imagee=request.files.get('imagee')
        category=request.form.get('category')
        filename=imagee.filename #getting the img name
        allowed=['jpg','png','jpeg','JPG','PNG','JPEG']
        imagee_deets=filename.split('.')
        ext=imagee_deets[-1]

        if filename:
            if ext in allowed:
                newname=secrets.token_hex(10)+ '.' +ext
                imagee.save('pkg/static/products/' + newname )
                prod=Product(prod_description=content,prod_price=price,prod_title=title,prod_image=newname,prod_catid=category)
                 
                db.session.add(prod)
                db.session.commit()
                flash('products uploaded successfully!',category='success')
                return redirect('/admin/')
            else:
                flash('file extension not allowed,allowed extension(jpg,png,jpeg)',category="error") 
                return redirect('/admin/')
        else:
            flash('You need to select a file for upload and provide title',category='warn')
            return redirect('/admin/')
        
            

@app.route('/adminlogout/')
def admin_logout():
    if session.get('adminonline') != None:
        session.pop('adminonline')
        flash('You Have Been logged out Successfully.',category='success')
        return redirect(url_for('admin_login'))
    
@app.route('/delete/<int:id>')
def delete(id):
        products = db.session.query(Product).get_or_404(id)
        actual_image = products.prod_image

        db.session.delete(products)
        db.session.commit()
        os.remove(f"pkg/static/products/{actual_image}")
        flash('Deletion was Successful', category='success' )
        return redirect('/admin/')


    