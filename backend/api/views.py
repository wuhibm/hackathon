from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import User, Message
from requests import post, get
import json
from django.http import HttpResponse, JsonResponse
from rest_framework.generics import RetrieveAPIView, ListAPIView
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

#Method for API calls
def get_data(endpoint):
    url = f"https://ifem-award-mchacks-2025.onrender.com/api/v1/{endpoint}"
    result = get(url)
    json_result = json.loads(result.content)
    return json_result


def register(request):
    if request.method == "POST":
        json_result = get_data("queue")
        patients = json_result["patients"]
        patient_ids = []
        for patient in patients:
            patient_ids.append(patient["id"])
        print(patient_ids)

        username = request.POST["username"]
        patient_id = request.POST["patient_id"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            #Password doesnt match confirmation
            return JsonResponse({"Error": "Passwords don't match"}, status=400)
        if patient_id not in patient_ids:
            #Not a patient
            return JsonResponse({"Error": "Invalid patient id"}, status=400)
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, password)
            user.save()
        except IntegrityError:
            #Username taken
            return JsonResponse({"Error": "Username is taken"}, status=400)
        login(request, user)
        return JsonResponse({"Message": "User successfully created"}, status=201)
    else:
        #TODO: Decide if other methods are allowed
        pass

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return JsonResponse({"Message": "User successfully logged in"}, status=201)
        else:
            return JsonResponse({"Message": "User successfully created"}, status=201)
    else:
        #TODO: Decide if other methods are allowed
        pass

def logout_view(request):
    logout(request)
    return JsonResponse({"Message": "User successfully logged out"}, status=201)

@login_required
def message_patients(request):
    content = request.POST["content"]
    channel = "patients"
    user = User.objects.get(username=request.user.username)
    Message.objects.create(content=content, sender=user, channel=channel)
    return JsonResponse({"Message": "Message successfully sent"}, status=201)

@login_required
def message_employees(request):
    content = request.POST["content"]
    channel = "employees"
    user = User.objects.get(username=request.user.username)
    Message.objects.create(content=content, sender=user, channel=channel)
    return JsonResponse({"Message": "Message successfully sent"}, status=201)

@login_required
def message_patient(request):
    content = request.POST["content"]
    user = User.objects.get(username=request.user.username)
    recipient = User.objects.get(patient_id=request.POST["recipient_id"])
    Message.objects.create(content=content, sender=user, recipient=recipient)
    return JsonResponse({"Message": "Message successfully sent"}, status=201)

class ChannelMessages(RetrieveAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    def get(self, request, channel):
        if request.auth != None:
            try:
                messages = Message.objects.filter(channel=channel)
                return Response(MessageSerializer(messages).data)
            except:
                Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            Response(status=status.HTTP_400_BAD_REQUEST)


class EmployeeMessages(RetrieveAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    def get(self, request):
        if request.auth != None:
            messages = []
            for message in Message.objects.all():
                if message.sender.role == "employee":
                    messages.append(message)
            return Response(MessageSerializer(messages).data)
        else:
            Response(status=status.HTTP_400_BAD_REQUEST)

class Messages(ListAPIView):
    serializer_class = MessageSerializer
