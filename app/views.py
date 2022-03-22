from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Login page
def login_page(request):
    
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        
        ## Authenticates against ORM
        user = authenticate(request, username = username, password = password)
        
        ## Username and password exists in ORM
        if user is not None:
            
            ## Queries from PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", [username])
                entry = cursor.fetchone()
                
                if entry[6] == 'user':
                    login(request, user)
                    return redirect('home',username=username)
                    
                elif entry[6] == 'admin':
                    login(request, user)
                    return redirect('admin')
                
        ## Username and password does not exist in ORM
        else:
            messages.error(request, 'Incorrect username or password.')
            return render(request, 'app/login.html')

    return render(request, 'app/login.html')

# Logout page
def logout_page(request):
    
    logout(request)
    
    return redirect('login')


def register(request):

    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        phone_number = request.POST.get('phonenumber')
        password = request.POST.get('password')
        confirm_password = request.POST.get('Confirm Password')
        
        if password != confirm_password:
            messages.error(request, "Those passwords didn't match. Try again")
            return render(request, 'app/register.html')
        
        with connection.cursor() as cursor:
               
            try: 
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)", [first_name, last_name, email, username, phone_number, password])
            # except Exception as e:
            #     string = str(e)

            #     if 'duplicate key value violates unique constraint "users_email_key"' in string:  
            #         messages.error(request, "This email has been taken. Try again")

                # elif 'new row for relation "users" violates check constraint "users_email_address_check"' in string:
                #     message = 'Please enter a valid email address!'
                # elif 'new row for relation "users" violates check constraint "users_mobile_number_check"' in string:
                #     message = 'Please enter a valid Singapore number!'

                return render(request, 'app/register.html')
            
            user = User.objects.create_user(email, password = password)
            user.save()
            messages.success(request, f'Account successfully created!')

            return redirect('home', username)

    return render(request, 'app/register.html')

# Create your views here.
def index(request):
    """Shows the main page"""

    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE username = %s", [request.POST['username']])
                
    if request.POST:            
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

@login_required(login_url = 'login')
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
    if request.POST:            
        if request.POST['action'] == 'deletePost':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM posts WHERE post_id = %s", [request.POST['post_id']])
            return redirect('mypost',username)  

    result_dict = {'currentuser': username}
    result_dict['records'] = posts
    return render(request,'app/mypost.html',result_dict)


def latestpost(request,username):
    """Shows the main page"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts")
        posts = cursor.fetchall()
    
def profile(request, username):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE username = %s", [username])
        posts = cursor.fetchall()

    result_dict = {'currentuser': username}
    result_dict['records'] = posts
    status = ''
    

    if request.POST:
        ## Check if username is already in the table
        with connection.cursor() as cursor:
            current_action = request.POST['action']
            cursor.execute("SELECT " + current_action + " FROM users WHERE username = %s ", [username])
            user = cursor.fetchone() 

            if user != None and user[0] == request.POST['old_'+ current_action] and request.POST['old_'+ current_action] != request.POST['new_'+ current_action]:
                cursor.execute("UPDATE users SET " + current_action + " = %s WHERE username = %s", [ request.POST['new_'+ current_action], username])
                status =  current_action + ' has been succesfully updated'
            else:
                status = current_action + 'of profile with username %s failed to change %s' % (username, current_action)


            result_dict[current_action + '_status'] = status
    return render(request,'app/profile.html',result_dict)
 
def adminView(request, username):
    """Shows the main page"""
    
    ## Use raw query to get a user
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        users = cursor.fetchone()
    result_dict = {'user': users}

    return render(request,'app/adminView.html',result_dict)

def postView(request, post_id):
    """Shows the main page"""
    
    ## Use raw query to get a post
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
        posts = cursor.fetchone()
    result_dict = {'post': posts}

    return render(request,'app/postView.html',result_dict)

def postEdit(request, post_id):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE posts SET pet = %s, breed = %s, date_of_post = %s, age_of_pet = %s, price = %s, description = %s, title = %s, status = %s, gender = %s WHERE post_id = %s"
                    , [request.POST['pet'], request.POST['breed'], request.POST['date_of_post'],
                        request.POST['age_of_pet'] , request.POST['price'], request.POST['description'], request.POST['title'], request.POST['status'], request.POST['gender'], post_id ])
            status = 'Post edited successfully!'
            cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/postEdit.html", context)


def userpostEdit(request, post_id,username):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE posts SET pet = %s, breed = %s, date_of_post = %s, age_of_pet = %s, price = %s, description = %s, title = %s, status = %s, gender = %s WHERE post_id = %s"
                    , [request.POST['pet'], request.POST['breed'], request.POST['date_of_post'],
                        request.POST['age_of_pet'] , request.POST['price'], request.POST['description'], request.POST['title'], request.POST['status'], request.POST['gender'], post_id ])
            status = 'Post edited successfully!'
            cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
    context["currentuser"]=username
 
    return render(request, "app/userpostEdit.html", context)
