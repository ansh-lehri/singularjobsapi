from rest_framework import generics,views
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate,logout
from .feed.feeds import UserOperationsOnNeo4j,UserOperationsOnMongoDB
from user_account.api.serializers import UserSerializer,UserProfileSerializer
from user_account.models import UserAccount,UserProfileModel
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from .utils import Util

import concurrent.futures
import jwt
import threading



def register_in_mongo(serializer):
    account = serializer.save()

def register_in_neo4j(email):
    neo_message = UserOperationsOnNeo4j().create_user(email)
    print(neo_message)

def cross():
    print(1)
    
def predict_in_neo4j(email,skills):
    neo_message = UserOperationsOnNeo4j().predict_similar_skills(email,skills.split(","))
    print(neo_message)
    
    
def push_into_mongodb(email,jobs,result):
    
    print("ANSH")
    try:
        mongo_message={}
        mongo_message['message'] = UserOperationsOnMongoDB().insert_jobs(email,jobs,"New")
        user = UserProfileModel.objects.get(email=email)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(user)
        print(user.user_jobs_list_exist)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        user.user_jobs_list_exist = "True"
        user.save()
        mongo_message['status']="200"
    except Exception as e:
        print(e)
        mongo_message = {'message':'Could not store job list.','status':"400"}
    result.append(mongo_message)
    print(mongo_message)
    #return mongo_message


def create_jobs(user, mongoops):
    
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%^^^^^^^^^^^^^^^^^^^")
    
    try:
        print(user)
        jobs = UserOperationsOnNeo4j().fetch_jobs(user,"No New User")
        print("ANSH KOVERHOOP")
    except Exception as e:
        print("Neo4j Error")
        print(e)
    print(jobs)
    
    try:
        mongo_message = mongoops.insert_jobs(user,jobs,"Not New")   
        print("ANSH")
        if len(jobs)!=0:
            email_body = 'Hi '+user + "\n\n"+'Hoorrraaayyyy!!!! Few jobs found you!!!!! Fresh batch of jobs is ready to have your attention. Feel free to apply anytime because you are boss of your own time.'
        else:
            email_body = 'Hi '+user + "\n\n"+ 'You can relax for now as no jobs suited to your skill set were available in this session. To improve your recommedations, you can try adding more skills to your profile'
        email_data = {'email_body': email_body, 'to_email': user,'email_subject': 'New Jobs'}
            
        Util.send_email(email_data)
    except Exception as e:
        print("Mongo Error")
        print(e)
    #print(mongo_message)
    #return mongo_message
    return

    

def update_mongodb(data):

    user = UserProfileModel.objects.get(email=data['email'])        
    user.technical_skills = data.get('technical_skills',user.technical_skills)
    user.soft_skills = data.get('soft_skills',user.soft_skills)
    user.job_types = data.get('job_types',user.job_types)
    user.subject_interest = data.get('subject_interest',user.subject_interest)
    user.linkedin_profile = data.get('linkedin_profile',user.linkedin_profile)
    
    user.save()
    return
    
def update_neo4j(data):
    
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(data['email'])
    print(data['technical_skills'].split(","))
    neo_message = UserOperationsOnNeo4j().update_user(data['email'],data['technical_skills'].split(","))
    return neo_message

        
def validate_email(email):
    account = None
    try:
        account = UserAccount.objects.get(email=email)
    except UserAccount.DoesNotExist:
        return None
    if account!=None:
        return email


def validate_username(username):
    account = None
    try:
        account = UserAccount.objects.get(username=username)
    except UserAccount.DoesNotExist:
        return None
    if account!=None:
        return username

def waste_call_intentional():
    print("MAAMA")
    pass
    
    
def send_email(email_data):
    Util.send_email(email_data)
    return

    
@api_view(['POST',])
@permission_classes([])
def registration_view(request):
    
    print("YES")
    #print(request.data.get('email').lower())
    if request.method=='POST':
        print("##############")
        data = dict()
        data['message']=[]
        
        email = request.data.get('email').lower()
        print("??????????????????????????")
        if validate_email(email)!=None:
            data['message'].append('Email already in use.')
            data['response']='Error'
            data['api_status']="404"
            print(type(data))
            
        username = request.data.get('username').lower()
        if validate_username(username)!=None:
            data['message'].append('Username already in use.')
            data['response']='Error'
            data['api_status']="404"
            print(type(data))
        
        if data['message']!=[]:
            return Response(data)
    
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
        
            t1 = threading.Thread(target=register_in_mongo,args=(serializer,))
            t2 = threading.Thread(target=register_in_neo4j,args=(str(serializer.data.get('email')),))
            
            t1.start()
            t2.start()
            
            t1.join()
            #t2.join()
            #account = serializer.save()
            
            
            user = UserAccount.objects.get(email=email)
            token = RefreshToken.for_user(user).access_token
            #token = str(jwt.encode({"user":user},settings.SECRET_KEY,algorithm="HS256"))            
            current_site = get_current_site(request).domain
            relativeLink = reverse('user_account:email-verify')
            absurl = 'http://'+current_site+relativeLink+'?token='+str(token)
            email_body = 'Hi '+user.username +" !!!"+ '\n\nWelcome to the Singular Jobs.\nUse the link below to verify your email and '+ "activate your account."+ "\n" + absurl
            email_data = {'email_body': email_body, 'to_email': user.email,'email_subject': 'Verify your email'}
            
            send_mail = threading.Thread(target=send_email,args=(email_data,))
            send_mail.start()
            
            if send_mail.is_alive():
                print("MAIL  SEBDING  PROCESS STILL  ALIVE !!!!!!!!!!!!")
            
            data['message'].append("User registered successfully.")
            data['email'] = serializer.data.get('email')
            data['username'] = serializer.data.get('username')
            data['api_status']="200"
        else:
            data = serializer.errors
            data['api_status']="404"
        
        print(type(data))
        print(type(Response(data)))
        return Response(data)        

@api_view(['GET',])
@permission_classes([])
def VerifyEmail(request):

    token = request.GET.get('token')
    print("YESSSSS")
    try:
        print("YYYAAAAAAAAAAASSSSSSSSSSSSSSSSSSSSSSSSS")
        print(token)
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
        print(payload)
        user = UserAccount.objects.get(id=payload['user_id'])
        if not user.is_verified:
            user.is_verified = True
            user.save()
            messages.success(request,"Your account is successfully verified. Continue to login.")
            return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/login')
        else:
            password = request.GET.get('password')
            user.set_password(password)
            user.save()
            print("password changed")
            list(messages.get_messages(request))
            
            # Problematic area where message is not getting displayed.
            # Dont know why is it happening.
            
            messages.success(request,"Your account is successfully verified. Continue to login with new password.")
            return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/redirect')
        
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error':"Activation Expired",'status':"400"})
    except jwt.exceptions.DecodeError as identifier:
        print(identifier)
        return Response({'error':"Invalid token",'status':"400"})
            

@api_view(['POST',])
@permission_classes([])
def login_view(request):
    
    if request.method=='POST':
        print("YES")
        email = request.data.get('username')
        password = request.data.get('password')
        
        print(email)
        print(password)
        account = authenticate(email=email,password=password)

        data = {}
        data['message']=[]

        if account:
            
            if not account.is_verified:
                data['api_status']="404"
                data['message'].append("You are not verified. Kindly verify your account first.")
                return Response(data)
            
            try:
                token = Token.objects.get(user=account)
            except Token.DoesNotExist:
                token = Token.objects.create(user=account)

            data['message'].append('Successfully authenticated.')
            data['email']=email
            data['token']=token.key
            print(account.username)
            data['username']=account.username
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            print(type(token.key))
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            data['api_status']="200"

        else:

            data['response']='Error'
            data['message'].append('Invalid Credentials.')
            data['api_status']="400"

        return Response(data)
        
        
        
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def create(request):

    if request.method=="POST":

        skills = {}
        print(request.POST)
        print("#######################################################################")
        print(request.data)
        print("#######################################################################")
        print()
        serializer = UserProfileSerializer(data = request.data)
        print("TRUE")
        print(serializer)
        if serializer.is_valid(): 
            serializer.save()
            print("-------------------------------------------------------------------------- ||||||||||||||||||||")
            print(request.data)
            print(type(request.data))
            data = request.data.dict()
            try:
                neo_message = update_neo4j(data)
                skills['api_status'] = "200"
            except Exception as e:
                print("Neo4j Error while registering user:")
                print(e)
                skills['api_status']="400"
                
            skills['updated_list'] = request.data.get('technical_skills')
            skills['message'] = "Working"
            skills['neo_message'] = "Koverhoop"
        else:
            skills = serializer.errors
            skills['api_status'] = "400"
        
        #Start producing similar skills to ones mentioned.
        t1 = threading.Thread(target=cross,args=())
        if skills['api_status']=="200":
            t2 = threading.Thread(target=predict_in_neo4j,args=(data['email'],data['technical_skills'],))
            t2.start()
        t1.start()
        
        return Response(skills)
        
@api_view(['PATCH',])
@permission_classes((IsAuthenticated,))
def update(request):

    if request.method=="PATCH":
        data = request.data
        print("I was there.")
        print(data)
        
         
        user_mongodb_thread = threading.Thread(target=update_mongodb,args=(data,))
        if 'technical_skills' in data.keys():
            user_neo4j_thread = threading.Thread(target=update_neo4j,args=(data,))
            user_neo4j_thread.start()
        
        user_mongodb_thread.start()
        
        user_mongodb_thread.join()
        user_neo4j_thread.join()
        
        # start producing results
        t1 = threading.Thread(target=cross,args=())
        if 'technical_skills' in data.keys():
            t2 = threading.Thread(target=predict_in_neo4j,args=(data['email'],data['technical_skills'],))
            t2.start()
            
        t1.start()
        
        return Response({'message':"Updated Successfully","status":"200"})

@api_view(['GET',])
@permission_classes([])
def update_neo4j_job_node_session(request):

    status = UserOperationsOnNeo4j().update_job_session()
    return Response(status)



@api_view(['POST',])
@permission_classes([])
def get_jobs(request):

    #close mongod connections is remaining.

    if request.method=="POST":
        response={}
        if request.data['user_jobs_list_exist']=="False":
            print("False")
            try:
                jobs_list = UserOperationsOnNeo4j().fetch_jobs(request.data['email'],"New User")
                # waste_Call thread can be deleted once confirmed of behavior.
                
                jobs = [{'jobs':jobs_list}]
                
                try:
                    result=[]
                    mongodb = threading.Thread(target=push_into_mongodb,args=(request.data['email'],jobs_list,result,))
                except Exception as e:
                    print(e)
                try:
                    waste_call = threading.Thread(target=waste_call_intentional,args=())
                except Exception as e:
                    print(e)
                print("BAABU BAABU BAAABU BAABU")
                #sort jobs accordingly and return response.
                
                mongodb.start()
                waste_call.start()
                response["message"] = "Done."
            except:
                jobs=[]
                response["message"] = "Oops! An error occurred"
            finally:
                response["recommend_jobs"] = jobs
                
        else:
            print("YES")
            try:
            
                jobs = UserOperationsOnMongoDB().fetch_jobs(request.data['email'])
                response["message"] = "Done"
            except:
                jobs=[]
                response["message"] = "Oops! An error occurred"
            finally:
                response["recommend_jobs"] = jobs
                
        return Response(response)
        
 
# runs every 6 hours.
@api_view(['POST',])
@permission_classes([])
def create_new_jobs(request):
    
    '''
    mongoops = UserOperationsOnMongoDB()
    users = mongoops.fetch_users()
    print(users)
    try:
        print("KHALEESi")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = {executor.submit(create_jobs, user, mongoops):user for user in users}
    except Exception as e:
        print("Threading Error")
        print(e)
    return  Response("DOne.")
    '''
    data = request.data
    user = data['mail']
    jobs_length = data['jobs_length']
    
    try:
        if jobs_length!=0:
            email_body = 'Hi '+user + "\n\n"+'Hoorrraaayyyy!!!! Few jobs found you!!!!! Fresh batch of jobs is ready to have your attention. Feel free to apply anytime because you are boss of your own time.'
        else:
            email_body = 'Hi '+user + "\n\n"+ 'You can relax for now as no jobs suited to your skill set were available in this session. To improve your recommedations, you can try adding more skills to your profile'
        email_data = {'email_body': email_body, 'to_email': user,'email_subject': 'New Jobs'}
            
        Util.send_email(email_data)
        print("mail sent successfully to: ")
        print(user)
        return Response({"message":"Email sent successfully"})
    except Exception as e:
        print("Mail error: ")
        print(e)
        return Response({"message":"Error in mail sending"})
    

@api_view(['POST',])
@permission_classes([])
def check_user_profile_exist(request):
    
    data = request.data
    profile_data = {}
    try:
        user = UserProfileModel.objects.get(email=data['email'])
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(type(user))
        print()
        print(user.technical_skills)
        profile_data['technical_skills'] = user.technical_skills
        profile_data['soft_skills'] = user.soft_skills
        profile_data['job_types'] = user.job_types
        profile_data['subject_interest'] = user.subject_interest
        profile_data['linkedin_profile'] = user.linkedin_profile
        print(user.user_jobs_list_exist)
        print(type(user.user_jobs_list_exist))
        if user.user_jobs_list_exist==None:
            profile_data['user_jobs_list_exist']=False
        else:
            profile_data['user_jobs_list_exist']=True
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& &&&&&&&&&")
        response = {'message':"User profile exists.","user_status":"200","user_profile":profile_data}
    except:
        profile_data['technical_skills'] = ""
        profile_data['soft_skills'] = ""
        profile_data['job_types'] = ""
        profile_data['subject_interest'] = ""
        profile_data['linkedin_profile'] = ""
        response = {'message':"User profile does not exists.","user_status":"400","user_profile":profile_data}
    finally:
        return Response(response)
        

@api_view(['PATCH',])
@permission_classes([])
def change_password(request):

    data = request.data
    try:
        user = UserAccount.objects.get(email=data['email'])
        if not user.is_verified:
            return response({"status":"404","message":"Account not verified. First verify the account."})
        
        user = UserAccount.objects.get(email=data['email'])
        token = RefreshToken.for_user(user).access_token
        #token = str(jwt.encode({"user":user},settings.SECRET_KEY,algorithm="HS256"))            
        current_site = get_current_site(request).domain
        relativeLink = reverse('user_account:email-verify')
        absurl = 'http://'+current_site+relativeLink+'?token='+str(token)+"&password="+data.get('new_password')
        email_body = 'Hi '+user.username +" !!!"+ '\n\nUse the link below to verify your email and '+ "to change your password."+ "\n" + absurl
        email_data = {'email_body': email_body, 'to_email': user.email,'email_subject': 'Verify your email'}
        
        
        send_mail = threading.Thread(target=send_email,args=(email_data,))
        send_mail.start()
        
        response = {"status":"201"}
    except:
        response = {"status":"400"}
    finally:
        return Response(response)
        
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def logout(request):

    request.user.auth_token.delete()
    logout(request)
    
    return Response({"message":"Successfully logged out."})


@api_view(['GET',])
@permission_classes([])
def urgent_mails(request):


    send_to_users = ["asthasachan02@gmail.com","deependra2199@gmail.com","katiyarvishal0011@gmail.com","shubhendras21@gmail.com","anshlehri0599@gmail.com"]

    for user in send_to_users:
        
        email_body = 'Hello '+user + "\n\n"+'We would like to apologize for the inconvenience caused while creating Singular Jobs profile earlier today because of LinkedIn URL. Also, during maintenance in night of 9 September 2021, we came around a bug, because of which your skills were not getting created as they were supposed to, which lead to either no or inappropriate job recommendations.\nWe have updated all your skills and have updated your job lists to best case possible.\n\n Once again, we would like to express our most sincere appologies for the inconvenience caused.\n\n\n Singular Jobs'
        email_data = {'email_body': email_body, 'to_email': user,'email_subject': 'Applogies for inconvenience while using the site.'}
        
        Util.send_email(email_data)
        print("mail sent successfully to: ")
        print(user)
        
    return Response({"msg":"Done"})