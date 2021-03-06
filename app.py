from fastapi import FastAPI, Response, status, HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


PostBase = schemas.PostBase
PostCreate = schemas.PostCreate
PostResponse = schemas.PostResponse


while True:
    try:
        cnnt = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='*****', cursor_factory=RealDictCursor)
        cursor = cnnt.cursor()
        print('Database connection was succesfull')
        break
    except Exception as error:
        print('Connection to database failed')
        print('Error: ', error)
        time.sleep(3)


def msg_404(id):
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f'Id:{id} does not exist')
    

@app.get('/')
def root():
    return {'Index': 'Main'}


#ALL POSTS
@app.get('/posts', response_model = List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    #cursor.execute('''SELECT * FROM posts ''')
    #posts = cursor.fetchall()    
    
    return posts


#CREATE POST
@app.post('/posts', status_code = status.HTTP_201_CREATED, response_model = PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute('''INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *''', (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # cnnt.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post


#GET POST
@app.get('/posts/{id}', response_model = PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute('''SELECT * FROM posts WHERE id = %s''', (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
         msg_404(id)
    
    return post


#DELETE POST
@app.delete('/posts/{id}', status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute('''DELETE FROM posts WHERE id = %s RETURNING*''', (str(id),))
    # delete_post = cursor.fetchone()
    # cnnt.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
       msg_404(id)
    post.delete(synchronize_session=False)
    db.commit()    

    return Response (status_code=status.HTTP_204_NO_CONTENT)


#UPDATE POST
@app.put('/posts/{id}', response_model = PostResponse)
def update_post(id: int, update_post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute('''UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *''', 
    #                 (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # cnnt.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
       msg_404(id)
    post_query.update(update_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
