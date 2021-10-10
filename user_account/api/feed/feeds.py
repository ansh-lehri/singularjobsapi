# This file should be part of views in API.
from .neoops import NeoOps
import environ
import os
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

class UserOperationsOnNeo4j:

    def __init__(self):
        pass

    def establish_connection(self):

        from neo4j import GraphDatabase, basic_auth
        try:
            db_driver = GraphDatabase.driver(os.environ.get("NEO4J_URI"),auth=(os.environ.get("NEO4J_USERNAME"), "Kheri@123"))
        except Exception as e:
            db_driver = ""
            print(e)
        finally:
            return db_driver

    def create_user(self,user_mail):

        neo = NeoOps()
        driver = self.establish_connection()
        print(driver)
        neo_message = {}
        try:
            message = neo.create_user(driver,user_mail)
            neo_message['message']="Your Profile is created."
        except Exception as e:
            print(e)
            neo_message['message']="Your profile could not be created."
        driver.close()
        return neo_message

    def update_user(self,user_mail, args):
        
        print("DEV")
        neo = NeoOps()
        driver = self.establish_connection()
        neo_message = {}
        print("ARGS -     ",args)
        try:
            neo.update_user_profile(driver,user_mail,args)
            neo_message['message']="Your Profile Update Successfully."
        except Exception as e:
            print(2)
            print(e)
            neo_message['message']="Could not update your profile."
        
        #neo.realted_skills(driver,user_mail)
        driver.close()
        return neo_message

        
    def fetch_jobs(self,user_mail,user_type):
        
        neo = NeoOps()
        driver = self.establish_connection()
        try:
            results = neo.find_rank_jobs(driver,user_mail,user_type)
            print(results)
        except Exception as e:
            print(e)
            results=[]
        #jobs_recommended = [job['job_id'] for job in results]
        driver.close()
        return results


    def predict_similar_skills(self,user_mail,user_skills):

        neo = NeoOps()
        driver = self.establish_connection()
        neo_message = {}
        try:
            neo.predict_skills(driver,user_mail,user_skills)
            neo_message['message']="Predicted skills for the user."
        except Exception as e:
            print(e)
            neo_message['message']="Could not predict skills for the user."
        driver.close()
        return neo_message
        
        
    def update_job_session(self):
        
        neo = NeoOps()
        driver = self.establish_connection()
        neo_message = {}
        try:
            print("Trying to update values")
            neo.update_job_session(driver)
            neo_message['message']="Successfully incremented session values."
        except Exception as e:
            print(e)
            neo_message['message']="Could not increment session values."
            neo_message['exact_error']=e
        
        driver.close()
        return neo_message


# need to optimise the class.
# 1. creating call to mongodb everytime. Not desirable. Create connection once for every user.
# 2. close mongodb connection.
class UserOperationsOnMongoDB:

    def __init__(self):
        self.client = None
        
        from pymongo import MongoClient
        
        db_name = "user_job"
        try:
            self.client = MongoClient(
                os.environ.get("MONGODB_URI") % (db_name)
            )
            print(self.client)
            print("Connection established to online mongodb.")

        except Exception as e:
            print(e)
            print("Online db not available. Connecting to local mongodb")
            self.client = MongoClient()
    
    
    
    def establish_connection(self,db_name):

        from pymongo import MongoClient
        
        try:
            self.client = MongoClient(
                os.environ.get("MONGODB_URI") % (db_name)
            )
            print(self.client)
            print("Connection established to online mongodb.")

        except Exception as e:
            print(e)
            print("Online db not available. Connecting to local mongodb")
            self.client = MongoClient()
            
            #return client
    
    
    def insert_jobs(self,email,jobs,status):
    
        
        #self.establish_connection("user_job")
        #print(mongodb_open)
        #print(type(mongodb_open))
        db_client = self.client["user_job"]
        collection = db_client["jobs"]
        
        if status=="New":
            try:
                print(status)
                collection.insert({"email":email,"jobs":jobs})
                print("Jobs inserted successfully.")
                collection.update({"email":email},{"$push":{"jobs":{"$each":[],"$sort":{"session":1,"score":-1}}}})
                print("Jobs sorted successfully.")
                return "Jobs inserted successfully."
            except Exception as e:
                print(e)
                print("Some error occurred.")
                return "Some error occurred."
        else:
            try:
                print("MOM")
                #collection.update({"email":email},{"$push":{"jobs":{"$each":jobs}}})
                #collection.update({"email":email},{"$inc":{"jobs.$.session":1}})
                collection.update({"email":email},{"$addToSet":{"jobs":{"$each":jobs}}})
                print("Jobs added successfully.")
                collection.update({"email":email},{"$push":{"jobs":{"$each":[],"$sort":{"session":1,"score":-1}}}})
                print("Jobs sorted successfully.")
                return "Jobs updated successfully."
            except:
                print("Some error occurred.")
                return "Some error occurred."
        
        
    def fetch_jobs(self,email):
    
        #self.establish_connection("user_job")
        #print(mongodb_open)
        #print(type(mongodb_open))
        db_client = self.client["user_job"]
        collection = db_client["jobs"]
        
        try:
            # can filter using session values. Say retrieve jobs for only latest 3 sessions etc...
            print(email)
            jobs = collection.find({"email":email})
            recommended_jobs = []
            
            for job in jobs:
                #print(job)
                recommended_jobs.append({"email":job["email"],"jobs":job["jobs"]})
            return recommended_jobs
        except:
            print("Some error occurred while retrieving jobs.")
            return "Some error occurred while retrieving jobs."
            
            
    def fetch_users(self):
        
        
        #self.establish_connection("user_job")
        #print(mongodb_open)
        #print(type(mongodb_open))
        db_client = self.client["user_job"]
        collection = db_client["jobs"]
        
        try:
            print("True")
            users=[]
            user_object = collection.find({})
            for user in user_object:
            #    print(user)
                 users.append(user['email'])
            return users
        except:
            return "Error"
        
        
        
        
        











'''
if __name__=="__main__":

    #response = update_user("anshlehrigola@gmail.com",["python","machine learning","mongodb","nlp"])
    #print(response)
    fetch_jobs("anshlehrigola@gmail.com","Yes")
'''


