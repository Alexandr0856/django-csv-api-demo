import csv
import requests

from datetime import datetime

from django.db import connection, transaction


def detect_column_type(value):
    if value == '':
        return 'TEXT'
    try:
        int_value = int(value)
        if -2147483648 <= int_value <= 2147483647:
            return 'INTEGER'
        else:
            return 'BIGINT'
    except ValueError:
        try:
            float(value)
            return 'DOUBLE PRECISION'
        except ValueError:
            try:
                datetime.strptime(value, '%Y-%m-%d')
                return 'BIGINT'
            except ValueError:
                return 'TEXT'


def create_dynamic_table(table_name, columns, sample_row):
    with connection.cursor() as cursor:
        column_definitions = []
        for col, value in zip(columns, sample_row):
            col_type = detect_column_type(value)
            column_definitions.append(f'"{col}" {col_type}')
        column_definitions = ", ".join(column_definitions)
        cursor.execute(f'CREATE TABLE "{table_name}" (id SERIAL PRIMARY KEY, {column_definitions})')


def convert_value(value, column_type):
    if value == '':
        return None
    if column_type in ['INTEGER', 'BIGINT']:
        try:
            return int(value)
        except ValueError:
            return None
    elif column_type == 'DOUBLE PRECISION':
        try:
            return float(value)
        except ValueError:
            return None
    elif column_type == 'BIGINT':
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return int(dt.timestamp())
        except ValueError:
            return None
    else:
        return value


def table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            );
        """)
        return cursor.fetchone()[0]


def drop_table(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')


def load_csv_in_batches(url, table_name, batch_size=1000, overwrite=False):
    response = requests.get(url)
    decoded_content = response.content.decode('utf-8').splitlines()
    reader = csv.reader(decoded_content)
    columns = next(reader)
    sample_row = next(reader)

    if overwrite and table_exists(table_name):
        drop_table(table_name)

    create_dynamic_table(table_name, columns, sample_row)

    column_types = [detect_column_type(value) for value in sample_row]

    with connection.cursor() as cursor:
        batch = []
        for row in reader:
            row = [convert_value(value, col_type) for value, col_type in zip(row, column_types)]
            batch.append(row)
            if len(batch) >= batch_size:
                placeholders = ", ".join(["%s"] * len(batch[0]))
                column_names = ", ".join([f'"{col}"' for col in columns])
                with transaction.atomic():
                    for batch_row in batch:
                        cursor.execute(f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})', batch_row)
                batch = []

        if batch:
            placeholders = ", ".join(["%s"] * len(batch[0]))
            column_names = ", ".join([f'"{col}"' for col in columns])
            with transaction.atomic():
                for batch_row in batch:
                    cursor.execute(f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})', batch_row)
