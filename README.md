# skygate_challenge1
Exams REST API

To run project follow nexts steps:
- `docker-compose build`
- `docker-compose up -d`
- `docker exec -it <service conatiner name> bash`
- `bash setup.sh`

This will prepopulate DB with fixtures and create set of users:
user        pass

user1       user
user2       user
user3       user
superuser   user

Each user is allowed to create exam and change it questions
Only owner can evaluate exam
Each user can submit exam only once
Users can display questions, exam results
Exam results can be filtered by user or by exam or both
Only admin user can update question definition
Each question has default value which if it matches user answer will evaluate that question and predict score

Example requests:
- GET exam?page_size=N    
page_size is manadatory param REsource will list existing exams with their questions

- POST exam/   body = {"q": [1,2,3]}  
This allow to create exam. 
Exam is containing questions, so q parameter is mandatory. q should be a list of questions ids

- PUT exam/{pk}/     body {"q":[1]}  
update exam questions, q is mandatory and is a list of questions ids

- DELETE exam/{pk}/  
resource deleting exam, pk is id of exam

-GET solve_exam?exam_id=3&user_name=admin  
exam_id and _user_name are optional  lists filtered set of answers

- POST  solve_exam/   body = {"exam_id":24,"answers": {"1":1}}  
Save user answers. 
Body params: exam_id id of exam, 
answers : a dictionary structed in that way: key is a question id value is answer text/number/bool/possibility id
    
- PUT   solve_exam/{pk}/  body = {"final_grade":24} 
Resource to evaluate exam

- GET  /question?page_size=2 
page_size is mandatory lists existing questions

- PUT /question_update/ body= {"max_grade": 12,"correct_answer": 1,    "one_of_poss": true}
Resource to update question parameters are optional, no all are needed

