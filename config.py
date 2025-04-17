import mysql.connector

class Config():
    domain = 'library.com'
    smtp_username = ""
    smtp_password = ""
    db_host = '127.0.0.1'
    user = 'root'
    password = 'your_password'  # Replace with your MySQL password
    database = 'librarymanagementdb'

    @classmethod
    def get_domain(cls):
        return cls.domain