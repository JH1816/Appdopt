from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Login page
def login_page(request):

    # with connection.cursor() as cursor:
    #     cursor.execute("SELECT * FROM users")
    #     users = cursor.fetchall()
    # for user in users:
    #     user_temp = User.objects.create_user(user[3], password = user[5])
    #     user_temp.save()
    
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
                    return redirect('home',username = username)
                    
                elif entry[6] == 'admin':
                    login(request, user)
                    return redirect('index')
                
        ## Username and password does not exist in ORM
        else:
            messages.error(request, 'Incorrect username or password.')
            return render(request, 'app/login.html')

    return render(request, 'app/login.html')

# Logout page
def logout_page(request):
    
    logout(request)
    
    return redirect('login')

# Register page
def register(request):

    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        phone_number = request.POST.get('phonenumber')
        password = request.POST.get('password')
        confirm_password = request.POST.get('Confirm Password')
        
        ## Checks if passwords are the same
        if password != confirm_password:
            messages.error(request, "Those passwords didn't match. Try again.")
            return render(request, 'app/register.html')
        
        with connection.cursor() as cursor:
               
            try: 
                ## Inserts into PostgreSQL database
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)", [first_name, last_name, email, username, phone_number, password])
            
            except Exception as e:

                string = str(e)

                ## Checks for uniqueness of email
                if 'duplicate key value violates unique constraint "users_email_key"' in string:  
                    messages.error(request, "This email has been taken. Try again.")

                ## Checks for uniqueness of username
                elif 'duplicate key value violates unique constraint "users_pkey"' in string:
                    messages.error(request, 'Username has been taken. Try again.')

                ## Checks for structure of email
                elif 'new row for relation "users" violates check constraint "users_email_check"' in string:
                    messages.error(request, 'Invalid email. Try again.')

                ## Checks for uniqueness of phone number
                elif 'duplicate key value violates unique constraint "users_phone_number_key"' in string:
                    messages.error(request, 'This phone number exists. Try again.')

                elif 'new row for relation "users" violates check constraint "users_phone_number_check"' in string:
                    messages.error(request, 'Invalid phone number. Try again.')

                return render(request, 'app/register.html')
            
            ## Registers into the ORM
            user = User.objects.create_user(username = username, password = password)
            user.save()

            messages.success(request, 'Account successfully created!')

            return redirect('login')

    return render(request, 'app/register.html')


# Home page
@login_required(login_url = 'login')
def home(request, username):    
    query_search = request.GET.get("psearch")
    query_price = request.GET.get("price")
    if not request.GET.get("gender"):
            query_gender = ""
    else:
        query_gender = "and gender = '"+request.GET.get("gender")+"'"

    if not request.GET.get("age_range"):
        query_age = ""
    elif request.GET.get("age_range") == "less than 1":
        query_age = "and cast(age_of_pet as int) <1"
    elif request.GET.get("age_range") == "1 to 3":
        query_age = "and cast(age_of_pet as int) <3 and cast(age_of_pet as int) >=1"
    elif request.GET.get("age_range") == "3 to 6":
        query_age = "and cast(age_of_pet as int) <6 and cast(age_of_pet as int) >=3"
    elif request.GET.get("age_range") == "6 to 10":
        query_age = "and cast(age_of_pet as int) <10 and cast(age_of_pet as int) >=6"
    else:
        query_age = "and cast(age_of_pet as int) >=10"

    print(request.GET)
    if request.GET:
        with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts WHERE (LOWER(description) LIKE LOWER('%%" + query_search + "%%') OR LOWER(location) LIKE LOWER('%%" + query_search + "%%') OR LOWER(username) LIKE LOWER('%%" + query_search + "%%') OR LOWER(title) LIKE LOWER('%%" + query_search + "%%'))" + query_gender + query_age+" ORDER BY PRICE "+ query_price,[query_gender])
                posts = cursor.fetchall()

        result_dict = {'currentuser': username}
        result_dict['records'] = posts
        return render(request,'app/home.html', result_dict)

    ## Checks if logged in user is the same
    elif request.user.username == username:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE status='AVAILABLE' ORDER BY post_id")
            posts = cursor.fetchall()
        result_dict = {'currentuser': username}
        result_dict['records'] = posts
        return render(request,'app/home.html', result_dict)
    else:
        messages.error(request, 'You have no access to this page')
        return redirect('home', username = request.user.username)

   

# Admin index page
def index(request):

    ## Delete all transactions, all posts as well as the user
    if request.POST:
        username = request.POST.get('username')
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                u = User.objects.get(username = username)
                u.delete()
                cursor.execute("DELETE FROM transactions WHERE seller_username = %s OR buyer_username = %s", [username, username])
                cursor.execute("DELETE FROM posts WHERE username = %s", [username])
                cursor.execute("DELETE FROM users WHERE username = %s", [username])

    ## Delete post            
    if request.POST:
        post_id = request.POST.get('post_id')            
        if request.POST['action'] == 'deletePost':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM transactions WHERE post_id = %s", [post_id])
                cursor.execute("DELETE FROM posts WHERE post_id = %s", [post_id])

    ## Delete transaction
    if request.POST:
        post_id = request.POST.get('post_id')            
        if request.POST['action'] == 'deleteTransaction':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM transactions WHERE post_id = %s", [post_id])
                cursor.execute("UPDATE posts SET status = 'AVAILABLE' WHERE post_id = %s", [post_id])

    ## Select all users into the table
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users ORDER BY username")
        users = cursor.fetchall()
    
    ## Select all posts into the table
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts ORDER BY post_id")
        posts = cursor.fetchall()
    
    ## Select all transactions into the table
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM transactions ORDER BY date_of_sale")
        transactions = cursor.fetchall()

    return render(request,'app/index.html',{'records': users, 'listing': posts, 'history': transactions})

# Adding users for Admin page
def addUser(request):

    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        with connection.cursor() as cursor:

            try: 
                ## Inserts into PostgreSQL database
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)", [first_name, last_name, email, username, phone_number, password])
            
            except Exception as e:

                string = str(e)

                ## Checks for uniqueness of email
                if 'duplicate key value violates unique constraint "users_email_key"' in string:  
                    messages.error(request, "This email has been taken. Try again.")

                ## Checks for uniqueness of username
                elif 'duplicate key value violates unique constraint "users_pkey"' in string:
                    messages.error(request, 'Username has been taken. Try again.')

                ## Checks for structure of email
                elif 'new row for relation "users" violates check constraint "users_email_check"' in string:
                    messages.error(request, 'Invalid email. Try again.')

                ## Checks for uniqueness of phone number
                elif 'duplicate key value violates unique constraint "users_phone_number_key"' in string:
                    messages.error(request, 'This phone number exists. Try again.')

                return render(request, 'app/add.html')

            user = User.objects.create_user(username = username, password = password)
            user.save()

            messages.success(request, 'Account successfully created!')

            return redirect('add')

    return render(request, 'app/add.html')

# Viewing users for Admin page
def adminView(request, username):
    
    ## Selects that specific user
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        users = cursor.fetchone()
    result_dict = {'user': users}

    return render(request,'app/adminView.html',result_dict)

# Editing users for Admin page
def edit(request, username):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        obj = cursor.fetchone()

    context["obj"] = obj
    status = ''
    # save the data from the form

    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        with connection.cursor() as cursor:

            try: 
                ## Updates PostgreSQL database
                cursor.execute("UPDATE users SET first_name = %s, last_name = %s, email = %s, phone_number = %s, password = %s WHERE username = %s"
                    , [first_name, last_name, email, phone_number, password, username])
            
            except Exception as e:

                string = str(e)

                ## Checks for uniqueness of email
                if 'duplicate key value violates unique constraint "users_email_key"' in string:  
                    messages.error(request, "This email has been taken. Try again.")

                ## Checks for structure of email
                elif 'new row for relation "users" violates check constraint "users_email_check"' in string:
                    messages.error(request, 'Invalid email. Try again.')

                ## Checks for uniqueness of phone number
                elif 'duplicate key value violates unique constraint "users_phone_number_key"' in string:
                    messages.error(request, 'This phone number exists. Try again.')

                return render(request, 'app/edit.html', context)

            u = User.objects.get(username = username)
            u.delete()
            user = User.objects.create_user(username = username, password = password)
            user.save()

            status = 'User edited successfully!'
            cursor.execute("SELECT * FROM users WHERE username = %s", [username])
            obj = cursor.fetchone()
            

    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/edit.html", context)


# View posts on admin page
def postView(request, post_id):
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
        posts = cursor.fetchone()
    result_dict = {'post': posts}

    return render(request,'app/postView.html',result_dict)

# Edit posts on admin page
def postEdit(request, post_id):
    
    context ={}

    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
        obj = cursor.fetchone()

    status = ''
    

    if request.POST:
        
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

    
# Create your views here.
def view(request, id,username):
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", [id])
        post = cursor.fetchone()
    if request.POST:
        if request.POST['action'] == 'BUY':
            with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM posts WHERE  post_id= %s", [id])
                    post = cursor.fetchone()
                    if post[9] == 'AVAILABLE' and post[1] != username:
                        cursor.execute("UPDATE posts SET status = 'NOT AVAILABLE' WHERE post_id = %s", [id])
                        cursor.execute("INSERT INTO  transactions VALUES (%s ,now(),%s,%s)",[ id,request.POST['seller'][:-1],username])
                        messages.success(request, "An order has been submitted. Please check 'My Orders' to contact the seller.")
                        return redirect('home', username = request.user.username)
                    else:
                        messages.error(request, "You cannot buy your own pet")
                        return redirect('home', username = request.user.username)

    result_dict = {'cust': post}
    result_dict['currentuser']=username

    return render(request,'app/view.html',result_dict)


@login_required(login_url = 'login')
def post(request,username):
    context = {}

    if request.POST:
        pet = request.POST.get('pet')
        breed = request.POST.get('breed')
        age_of_pet = request.POST.get('age_of_pet')
        price = request.POST.get('price')
        description = request.POST.get('description')
        title = request.POST.get('title')
        gender = request.POST.get('gender')
        location = request.POST.get('location')
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(post_id)+1 FROM posts")
            post = cursor.fetchone()
            
            cursor.execute("INSERT INTO posts VALUES (%s, %s, %s, %s, now(), %s,%s,%s,%s,'AVAILABLE',%s, %s)"
                    , [post, username, pet, breed, age_of_pet, price, description, title, gender, location])
            messages.success(request, 'Post created!')

    context['currentuser'] = username
 
    return render(request, "app/post.html", context)

@login_required(login_url = 'login')
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


@login_required(login_url = 'login') 
def profile(request, username):
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE username = %s", [username])
        posts = cursor.fetchall()
        cursor.execute("SELECT * FROM ratings WHERE username = %s", [username])
        users = cursor.fetchone()
    
    
    result_dict = {'currentuser': username}
    result_dict['records'] = posts
    result_dict['users'] = users
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

@login_required(login_url = 'login')
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
            cursor.execute("UPDATE posts SET pet = %s, breed = %s, age_of_pet = %s, price = %s, description = %s, title = %s, status = %s, gender = %s, location = %s WHERE post_id = %s"
                    , [request.POST['pet'], request.POST['breed'],
                        request.POST['age_of_pet'] , request.POST['price'], request.POST['description'], request.POST['title'], request.POST['status'], request.POST['gender'], request.POST['location'], post_id ])
            status = 'Post edited successfully!'
            cursor.execute("SELECT * FROM posts WHERE post_id = %s", [post_id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
    context["currentuser"]=username
 
    return render(request, "app/userpostEdit.html", context)

@login_required(login_url = 'login')
def average(request,username):
    """Shows the main page"""
    with connection.cursor() as cursor:
        cursor.execute('''
        select pet,breed,Round(avg(price),2) from posts
        group by(pet,breed)
        order by pet''')
        breeds = cursor.fetchall()


    result_dict = {'currentuser': username}
    result_dict['breeds'] = breeds

    return render(request,'app/average.html',result_dict)

@login_required(login_url = 'login')
def orders(request,username):
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM pending_transactions WHERE seller_username = %s",[username])
        posts = cursor.fetchall()
        if request.POST:            
            if request.POST['action'] == 'Accept':
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM posts WHERE post_id = %s", [request.POST['post_id']])
                return redirect('orders',username)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM pending_transactions WHERE buyer_username = %s",[username])
        posts = cursor.fetchall()
        if request.POST:
            if request.POST['action'] == 'Cancel':
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM transactions WHERE post_id = %s", [request.POST['post_id']])
                    cursor.execute("UPDATE posts SET status = 'AVAILABLE' WHERE post_id = %s",[request.POST['post_id']])
                return redirect('orders', username)

    result_dict = {'currentuser': username}
    result_dict['records'] = posts
    return render(request,'app/orders.html',result_dict)