class NeoOps:

    def __init__(self):
        pass

    def update_user_profile(self, driver, user_mail, args):
        
        print("SONA")
        with driver.session() as session:
            tx = session.begin_transaction()
            result = self.create_relationship(tx,user_mail,args)
            tx.commit()
            tx.close()            
        print("ISHWARI")    
        return
        
    
    def find_rank_jobs(self,driver,user_mail,user_type):
        jobs=[]
        
        with driver.session() as session:
            tx = session.begin_transaction()
            result = self.compute_job_scores(tx,user_mail,user_type)
            tx.commit()
            tx.close()
            
            jobs=result
        return jobs
               
    def create_user(self,driver,user_mail):
        
        with driver.session() as session:
            session.run("CREATE (n:User{mail:$user_mail}) return n",user_mail=user_mail)

        return ({"message":"User Created in Neo4j"})
        
        
    def predict_skills(self,driver,user_mail,user_skills):
    
        with driver.session() as session:
            tx = session.begin_transaction()
            results = self.compute_user_skill_scores(tx,user_mail)
            skills = [skill["name"] for skill in results if skill["name"] not in user_skills]
            task_stats = self.create_user_skill_predicted_relationship(tx,user_mail,skills)
            tx.commit()
            tx.close()
            print("??????????????????????????????????/")
            print(skills)
            print()
            print()
            print(results)
        
        return
    
    def update_job_session(self,driver):
        
        print("zyo")
        with driver.session() as session:
            tx = session.begin_transaction()
            records = tx.run("MATCH (n:JOB) set n.session = n.session + 1 return n limit 10")
            for record in records.data():
                print(record)
            tx.commit()
            tx.close()
            
        return
    
    def find_user_node(self,tx,user_mail):

        record = tx.run("MATCH (n:User{mail:$user_mail}) RETURN n",user_mail=user_mail)
        return record
        
    
    def create_relationship(self,tx,user_mail,args):
        
        print("ERICA")
        record = tx.run("match(node:User{mail:$user_mail}) UNWIND $args as skill match(n:JOB_ENTITIES{name:skill}) merge (node)-[:INTERESTED_IN]->(n)",user_mail=user_mail,args=args)
        record.consume()
        return
        

    def create_user_skill_predicted_relationship(self,tx,user_mail,args):

        record = tx.run("match(node:User{mail:$user_mail}) UNWIND $args as skill match(n:JOB_ENTITIES{name:skill}) merge (node)-[:MIGHT_BE_INTERESTED_IN]->(n)",user_mail=user_mail,args=args)
        record.consume()
        return        
                
    
    # need to change this query a bit in terms of limit.
    def compute_job_scores(self,tx,user_mail,user_type):

        jobs = []
        
        if user_type=="New User":
            records = tx.run("MATCH (n:User{mail:$user_mail}),(p:JOB) with n,collect(p) as jobs unwind jobs as job with job.job_id as job_id, job.job_title as job_title, job.company_name as company_name, job.job_url as url, job.session as session, job.listed_on as listed_on, job.short_desc as short_desc, gds.alpha.linkprediction.adamicAdar(n,job) as score where score>0 return job_id,job_title,company_name,url,session,listed_on,short_desc,score order by score desc limit 40",user_mail=user_mail)
        else:
            records = tx.run("MATCH (n:User{mail:$user_mail}),(p:JOB{session:1}) with n,collect(p) as jobs unwind jobs as job with job.job_id as job_id, job.job_title as job_title, job.company_name as company_name, job.job_url as url, job.session as session, job.listed_on as listed_on, job.short_desc as short_desc, gds.alpha.linkprediction.adamicAdar(n,job) as score where score>0 return job_id,job_title,company_name,url,session,listed_on,short_desc,score order by score desc limit 40",user_mail=user_mail)
        for record in records.data():
            jobs.append(record)
            
        return jobs
        
        
    def compute_user_skill_scores(self,tx,user_mail):
    
        skills = []
        records = tx.run("MATCH (n:User{mail:$user_mail}),(p:JOB_ENTITIES) with n,collect(p) as skills unwind skills as skill return skill.name as name, gds.alpha.linkprediction.resourceAllocation(n,skill) as score order by score desc limit 10",user_mail=user_mail)
        for record in records.data():
            skills.append(record)
        trial = records.values()
        print("*************")
        print(trial)
        return skills