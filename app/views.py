from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.
def index(request):
    """Shows the main page"""

    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM customers WHERE customerid = %s", [request.POST['id']])

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts ORDER BY post_id")
        posts = cursor.fetchall()

    result_dict = {'records': posts}

    return render(request,'app/index.html',result_dict)

# Create your views here.
def home(request,username):
    """Shows the main page"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts ORDER BY post_id")
        posts = cursor.fetchall()

    result_dict = {'currentuser': username}
    result_dict['records'] = posts
    return render(request,'app/home.html',result_dict)

# Create your views here.
def view(request, id,username):
    """Shows the main page"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [id])
        post = cursor.fetchone()
    result_dict = {'cust': post}
    result_dict['currentuser']=username

    return render(request,'app/view.html',result_dict)

# Create your views here.
def add(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [request.POST['customerid']])
            customer = cursor.fetchone()
            ## No customer with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO customers VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['dob'] , request.POST['since'], request.POST['customerid'], request.POST['country'] ])
                return redirect('index')    
            else:
                status = 'User with ID %s already exists' % (request.POST['customerid'])


    context['status'] = status
 
    return render(request, "app/add.html", context)

# Create your views here.
def edit(request, id):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE customers SET first_name = %s, last_name = %s, email = %s, dob = %s, since = %s, country = %s WHERE customerid = %s"
                    , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                        request.POST['dob'] , request.POST['since'], request.POST['country'], id ])
            status = 'Customer edited successfully!'
            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/edit.html", context)


def register(request):
    context = {}
    status = ''

    if request.POST:
        ## Check if username is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE  username= %s ", [request.POST['username']])
            customer = cursor.fetchone()
            ## No customer with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['username'] , request.POST['phonenumber'], request.POST['password']])
                messages.success(request, f'Account successfully created!')
                return redirect('home',username=request.POST['username'])    
            else:
                status = 'User with username %s already exists' % (request.POST['username'])


    context['status'] = status
 
    return render(request, "app/register.html", context)

def login(request):
    context = {}
    status = ''
    if request.POST:
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE  username= %s AND  password =%s", [request.POST['username'], request.POST['password']])
            customer = cursor.fetchone()
            ## No user with that user name or wrong password
            if customer != None:
                return redirect('home',username=request.POST['username'])    
            else:
                status = 'Wrong password or username'


    context['status'] = status
    return render(request, 'app/login.html', context)


def post(request,username):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if username is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM posts WHERE  post_id= %s ", [request.POST['post_id']])
            post = cursor.fetchone()
            ## No post with same id
            if post == None:
                cursor.execute("INSERT INTO posts VALUES (%s, %s, %s, %s, now(), %s,%s,%s,%s,'AVAILABLE',%s)"
                        , [request.POST['post_id'], username,request.POST['pet'], request.POST['breed']
                        , request.POST['age_of_pet'], request.POST['price'],
                           request.POST['description'],request.POST['title'],request.POST['gender']])
                status = 'Post with post_id %s has been succesfully posted' % (request.POST['post_id'])
            else:
                status = 'Post with post_id %s  already exists' % (request.POST['post_id'])


    context['status'] = status
    context['currentuser'] = username
 
    return render(request, "app/post.html", context)

