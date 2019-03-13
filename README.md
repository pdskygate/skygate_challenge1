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
