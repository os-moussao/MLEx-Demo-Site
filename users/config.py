import os

db_url = 'postgres://ncbgirnmtdgnuh:a8f676d87406e397c74bcb30652260a2c1c1b44fae7ca66831ac8f9f3baadc8b@ec2-54-87-112-29.compute-1.amazonaws.com:5432/d8c61rvunapvh4'

class Config:
    SQLALCHEMY_DATABASE_URL = db_url