# Placement Portal Enterprise history
PB -> Placement Portal Backend

## Ticket PB-0001
### Implement Authentication advancement
Aim: To implement Email/Password JWT HTTP-only


## Ticket PB-0002
### Implement User management admin
Aim:
1. Add Bulk user creation/updation/deletion/export
2. Email notification on account creation

## Ticket PB-0003
### Implement Forgot Password
Forgot Password, 2FA

## Ticket PB-0004
### Implement Notification system, primarily with Emails


## Ticket PB-0005
### Implement base of the Placement Portal
1. Here, company user will create job posts
2. Student of that course will see the job post
3. Student will apply to job post
4. Company will see the application
5. Student Resume information in DB


## PB-0006 -> Advancement in services
Here, we have to add all enterprise containers to make task faster and reliable. Following are the containers:-
1. Celery
2. RabbitMQ
3. Redis
4. Flower
5. Beat (optional)

and, implement email as a celery task

## PB-0007 -> Email Management micro service

## PB-0008 -> Resume Parsing and snapshot


Things to be implemented at Student side:
1. Application Listing - done
2. Application Description - done
3. Resume mgmt (restrict number of resume uploaded by the student, and size, and CRUD) - add config for resume - working, but once application created, we cannot remove the resume from the system, need to fix this part, because it's foreign key to application.-  on delete set NULL
4. Job and Application page filters
5. Profile - Done



resume upload and parsing scenarios:-
1. Resume uploaded by student -> resume is now parsing -> applied for job before parsing completes -> then application has resume, but no meta data there
2. Resume uploaded by student -> resume is now parsing -> applied for job before parsing completes -> deletes the resume -> employer opens the application
3. Resume uploaded by student -> resume is parsing -> parsing completed -> applied for job -> employer opens the resume, and watching it -> meanwhile, student deletes the resume -> then, employer clicks on download resume
4. resume uploaded -> parsing task failed -> applied for job -> employer opens the application
5. resume uploaded -> parsing the resume -> applied for job -> parser still running, but employer opens the application
6. resume uploaded -> parsing the resume -> applied for job -> parsing commpleted, but only partial or no information can be extracted, as the resume is not as we want for the parser (not ATS friendly) -> partial or no information shown at employer side => Tell what is ATS friendly, and what is not! -> We can hide the non-ATS friendly resume from the employer, but show it to the student, so they can reapply, better, hide non-ATS friendly metadata
7. multipage resume uploaded -> parser (need to throw error for being multipage resume) -> how will the student know? -> will get reflected at application end, but student can't delete the application => we need to tell what is ATS friendly and what is not! -> We can hide the non-ATS friendly resume from the employer, but show it to the student, so they can reapply -> We can hide the non-ATS friendly resume from the employer, but show it to the student, so they can reapply with better resume, better, hide non-ATS friendly metadata

Hide the resume, until it is not completely processed.
1. Then, parser parsing the resume for forever... (BUG)
2. what if parser crashed, and status didn't reflected at the resume table.
3. Fake delete for application, at student end, to reapply with ATS friendly resume

8. student uploaded resume -> resume parsing -> applied for job -> employer deleted the job -> not allowed
9. student uploaded resume -> resume parsing -> applied for job -> company deactivated itself -> not allowed
10. student uploaded resume -> resume parsing -> applied for job -> student deactivated itself -> not allowed
11. Student uploaded resume, resume contains only photos -> resume parsing not detects any text

17 July 2026:-
1. For MVP, keep things as it is, just add config to increase the limit of resumes.



22 July, 2026:-
Phase 2: Make it real
- application page created with pdf upload - Done
- set null for resume delete
- profile information
- extract information from resume -> see the scenarios
- resume parsing at upload stage, not on every application creation
- ATS friendly resume
- limit number of resumes config, with redis caching
- Forgot Password flow
- Email notifications
- tasks management
- server caching with redis
- Bulk Student creation
- AWS deployment

pb-0005 -> MVP is completed!
pb-0006 -> Advancement in services

Here, we have to add all enterprise containers to make task faster and reliable. Following are the containers:-
1. Celery
2. RabbitMQ
3. Redis
4. Flower
5. Beat (optional)

and, implement email as a celery task
