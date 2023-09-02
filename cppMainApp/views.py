import pandas
import io
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from psycopg2.extras import NamedTupleCursor

# from django.db import connection
# Create your views here.


class GetAllTablesNames(APIView):
    def get(self, request):
        # connection = create_connection()
        connection = request.db_connection

        cursor = connection.cursor()
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        # query = f"""
        #     SELECT TABLE_NAME
        #     FROM INFORMATION_SCHEMA.TABLES
        #     WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG='postgres'
        # """

        cursor.execute(query)

        table_names = [row[0] for row in cursor.fetchall()]
        # cursor.close()
        # connection.close()
        return render(request, 'table.html', {"tables": table_names})


class GetAllDataSpecificTable(APIView):
    def get(self, request, table_name):
        connection = request.db_connection
        cursor = connection.cursor()
        query = f'SELECT * from public."{table_name}";'
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]

        # Fetch all rows and convert to list of dictionaries
        data = cursor.fetchall()
        result_list = [{column_names[i]: value for i, value in enumerate(row)} for row in data]
        print(result_list)


        # data = cursor.fetchall()
        rows_value = []
        for row in data:
            temp_row = []
            for value in row:

                temp_row.append(value)
            rows_value.append(temp_row)

        column_names = [desc[0] for desc in cursor.description]

        # query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';"
        # cursor.execute(query)
        # print(cursor.fetchall())
        # column_names = [row[0] for row in cursor.fetchall()]
        print(column_names)

        return render(request, 'table_detail.html', {"data": rows_value, 'columns': column_names, 'table_name': table_name})
        # return JsonResponse({"data": data}, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateDataSpecificTableViaUniqueIdentification(APIView):
    def post(self, request):
        update_values = request.data.get('data', '("7", "case 1", "Description 1", "false", "2023-05-31T14:36:15.526+05:30", "null")')
        condition = request.data.get('condition', 'id = 1')
        

        connection = request.db_connection
        cursor = connection.cursor()
        # query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{request.GET.get('table_name', 'pdi_app_case')}';"
        # cursor.execute(query)

        
        set_values = update_values
        sql_query = f"UPDATE common.{request.data.get('table_name', 'pdi_app_case')} SET {set_values} WHERE {condition};"
        cursor.execute(sql_query)

        connection.commit()
        print("Rows updated successfully!")
        return JsonResponse({"data": "Updated"}, safe=False)

class UpdateDataSpecificTableViaFile(APIView):
    def post(self, request):
        # connection = request.db_connection
        cursor = request.db_connection.cursor()

        query = f"SELECT column_name FROM information_schema.columns where table_name = '{request.GET.get('table_name', 'pdi_app_case')}';"
        cursor.execute(query)
        table_columns = [row[0] for row in cursor.fetchall()]

        excel_data = request.FILES.get('File')

        excel_data = excel_data.read()
        df = pandas.read_csv(io.BytesIO(excel_data))
        dataframe = df.to_json(orient='records')

        value_list = dataframe.values.tolist()
        for value in value_list:
            query

        # for index, row in dataframe.iterrows():
        #     values = {}
        #     for i in zip(list(index),list(row)):
        #         values[i[0]] = i[1]
        #     print(values)

@method_decorator(csrf_exempt, name='dispatch')
class delete_table(APIView):
    def post(self, request):
        table_name = request.POST.get("Table_name")
        connection = request.db_connection
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM "{table_name}";')
        # cursor.close()
        connection.commit()
        return GetAllTablesNames().get(request)
    
@method_decorator(csrf_exempt, name='dispatch')
class delete_entry(APIView):
    def post(self, request):
        data_string=request.POST.get("case_id")
        table_name=request.POST.get("case_table_name")
        connection = request.db_connection
        cursor = connection.cursor()
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';")
        column_names = [colmn[0] for colmn in cursor.fetchall()]
        Pk_index=column_names.index('personid')
        #print(cursor.execute(f"SELECT conrelid::regclass AS table_name, conname AS primary_key, pg_get_constraintdef(oid) FROM pg_constraint WHERE  contype = 'p' AND connamespace = 'public'::regnamespace AND conrelid::regclass::text = 'team';"))
        # print(cursor.execute(f"SELECT a.attname AS column_name FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) WHERE i.indrelid = 'persons'::regclass AND i.indisprimary;"))
        # query = """
        # SELECT conrelid::regclass AS table_name,
        #        conname AS primary_key,
        #        pg_get_constraintdef(oid)
        # FROM pg_constraint
        # WHERE contype = 'p'
        #   AND connamespace = 'public'::regnamespace
        #   AND conrelid::regclass::text = 'team';
        # """
        # cursor.execute(query)
        # results = cursor.fetchall()
        # for row in results:
        #     table_name, primary_key, constraint_def = row
        #     print("Table Name:", type(constraint_def))
        data_list=data_string.split(',')
        cursor.execute(f"DELETE FROM {table_name} WHERE personid = {data_list[Pk_index]}")
        connection.commit()
        return GetAllDataSpecificTable().get(request,table_name)
    
@method_decorator(csrf_exempt, name='dispatch')
class update_entry(APIView):
    def post(self, request):
        table_name=request.POST.get("entry_updation_table_name")
        old_data_string=request.POST.get("old_entry")
        old_data_list=old_data_string.split(',')
        connection = request.db_connection
        cursor = connection.cursor()
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';")
        column_names = [colmn[0] for colmn in cursor.fetchall()]
        index=column_names.index('personid')
        insertion_data=''
        for column in column_names:
            temp = request.POST.get(f"set{column}")
            if column == "personid":
                pass
            elif insertion_data:
                insertion_data = insertion_data + ',' + column + '=' + "'" + temp + "'"
            else:
                insertion_data = column + '=' +  "'" + temp + "'"
        cursor.execute(f"UPDATE {table_name} SET {insertion_data} WHERE personid = {old_data_list[index]};")

        connection.commit()
        return GetAllDataSpecificTable().get(request,table_name)
        









        
            
            



