from django.db import connection, OperationalError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import CSVMetaData
from api.utils import load_csv_in_batches


class CSVUploadView(APIView):
    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        table_name = request.data.get('table_name')
        overwrite = request.data.get('overwrite', False)

        if not url or not table_name:
            return Response({"error": "URL and table_name are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            load_csv_in_batches(url, table_name, overwrite=overwrite)
            try:
                CSVMetaData.objects.create(filename=url)
            except OperationalError:
                pass
            return Response({"message": "Data loaded successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DynamicDataView(APIView):
    def get(self, request, *args, **kwargs):
        table_name = request.query_params.get('table')
        filters = {key: value for key, value in request.query_params.items() if key != 'table'}

        where_clause = " AND ".join([f"{key} = %s" for key in filters.keys()])
        query = f"SELECT * FROM {table_name} WHERE {where_clause}"

        with connection.cursor() as cursor:
            cursor.execute(query, list(filters.values()))
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        result = [dict(zip(columns, row)) for row in rows]
        return Response(result)
