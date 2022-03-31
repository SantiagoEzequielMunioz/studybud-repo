#USUARIOS!!!!
#erik - erik1234 // santiago - 1234
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, Room, Topic
from .forms import RoomForm

# rooms = [
#     {'id':1,'name':'Lets learn python'},
#     {'id':2,'name':'Design with me'},
#     {'id':3,'name':'Frontend developers'}
# ]

def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User does not exists')
        user = authenticate(request,username=username,password=password)    
    
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
           messages.error(request,'Username OR password does not exists')


    context = {'page':page}
    return render(request,'base/login_register.html',context)

def logout_user(request):
    logout(request)
    return redirect('home')

def register_page(request):
    
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occurred during registration')

    return render (request,'base/login_register.html',{'form':form})


def home(request):
    if request.GET.get('q') != None:    #otra forma: q = request.GET.get('q') if request.GET.get('q') != None else ''
        q = request.GET.get('q')
    else:
        q=''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |  # | es un or, & es un and, solo se puede usar asi
        Q(name__icontains=q) |
        Q(name__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

def room(request,pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    room_msg = room.message_set.all() #message es el model, esta es la forma de pedir el set de messages que estan referidos a cierto room
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context = {'room':room,'room_msg':room_msg,'participants':participants} #está demas esto pero se hace para no joder la funcionalidad. un refresh forzado
            
    return render(request,'base/room.html',context)

def user_profile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user':user,'rooms':rooms,
            'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)


@login_required(login_url='login') # decorador importado, si no está registrado lo devuelve a esa url
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home') #este home es name='home' de urls

    context= {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def update_room(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def delete_msg(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})