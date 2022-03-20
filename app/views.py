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
                cursor.execute("DELETE FROM users WHERE username = %s", [request.POST['username']])
                
        if request.POST['action'] == 'deletePost':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM posts WHERE post_id = %s", [request.POST['post_id']])

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users ORDER BY username")
        users = cursor.fetchall()
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts ORDER BY post_id")
        posts = cursor.fetchall()

    return render(request,'app/index.html',{'records': users, 'listing': posts})

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
    status=''
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [id])
        post = cursor.fetchone()
    if request.POST:
        with connection.cursor() as cursor:
                cursor.execute("SELECT status FROM posts WHERE  post_id= %s ", [id])
                post = cursor.fetchone()[0]
                if post == 'AVAILABLE':
                    cursor.execute("UPDATE posts SET status = 'NOT AVAILABLE' WHERE post_id = %s", [id])
                    cursor.execute("INSERT INTO  transactions VALUES (%s ,now(),%s,%s)",[ id,request.POST['seller'][:-1],username])
                    status = 'Pet with post_id %s has been succesfully brought' % (id)
                else:
                    status = 'Pet with post_id %s is not available' % (id)
    result_dict = {'cust': post}
    result_dict['currentuser']=username
    result_dict['status'] = status

    return render(request,'app/view.html',result_dict)

# Create your views here.
def add(request):
    context = {}
    status = ''

    if request.POST:
        ## Check if username is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE username = %s", [request.POST['username']])
            users = cursor.fetchone()
            ## No same username
            if users == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['username'] , request.POST['phone_number'], request.POST['password'] ])
                return redirect('index')    
            else:
                status = 'User with username %s already exists' % (request.POST['username'])


    context['status'] = status
 
    return render(request, "app/add.html", context)

# Create your views here.
def edit(request, username):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET first_name = %s, last_name = %s, email = %s, phone_number = %s, password = %s WHERE username = %s"
                    , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                        request.POST['phone_number'] , request.POST['password'], username ])
            status = 'User edited successfully!'
            cursor.execute("SELECT * FROM users WHERE username = %s", [username])
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

def mypost(request,username):
    """Shows the main page"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE username = %s ORDER BY post_id",[username])
        posts = cursor.fetchall()

    result_dict = {'currentuser': username}
    result_dict['records'] = posts
    return render(request,'app/mypost.html',result_dict)


def latestpost(request,username):
    """Shows the main page"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts")
        posts = cursor.fetchall()
    
def adminView(request, username):
    """Shows the main page"""
    
    ## Use raw query to get a user
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        users = cursor.fetchone()
    result_dict = {'user': users}

    return render(request,'app/adminView.html',result_dict)
