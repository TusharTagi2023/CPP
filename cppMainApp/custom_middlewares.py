# from django.db import connection
import psycopg2
import os

class OpenPostgresConnectionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("in the middleware")
        # Open Postgres connection
        db_params = {
            'dbname': os.getenv('data_db_database'),
            'user': os.getenv('data_db_user'),
            'password': os.getenv('data_db_pass'),
            'host': os.getenv('data_db_host'),
            'port': os.getenv('data_db_port'),
        }


        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        request.db_connection = connection
        print(request.db_connection)
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """

        cursor.execute(query)

        table_names = cursor.fetchall()
        # print(table_names)
        return self.get_response(request)

class ClosePostgresConnectionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Close Postgres connection
        if hasattr(request, 'db_connection'):
            request.db_connection.close()
        print("Closed")
        return response
