from flask import g


class CRUD:
    def __init__(self, table_name):
        self.table_name = table_name
        self.mysql = g.db

    # create a new record
    def create(self, **kwargs):
        """Insert a new record into the table."""
        columns = ", ".join(kwargs.keys())
        values_placeholder = ", ".join(["%s"] * len(kwargs))
        values = tuple(kwargs.values())
        query = (
            f"INSERT INTO {self.table_name} ({columns}) VALUES ({values_placeholder})"
        )

        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query, values)
            self.mysql.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return {"status": "success", "data": last_id}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # get a record by a specific column
    def get_by_column(self, column, value):
        """Get a record by a specific column."""
        valid_columns = self._get_valid_columns()
        if column not in valid_columns:
            raise ValueError(f"Invalid column name: {column}")
        query = f"SELECT * FROM {self.table_name} WHERE `{column}` = %s ORDER BY created_at DESC"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query, (value,))
            record = cursor.fetchone()
            if record:
                columns = [desc[0] for desc in cursor.description]
                record = dict(zip(columns, record))
            cursor.close()
            if record:
                return {"status": "success", "data": record}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # get exit or not
    def exists(self, column, value):
        """Check if a record exists."""
        query = f"SELECT * FROM {self.table_name} WHERE {column} = %s"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query, (value,))
            result = cursor.fetchone()
            cursor.close()
            return {"status": "success", "data": bool(result)}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # update a record
    def update(self, record_id, **kwargs):
        """Update a record."""
        columns = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = tuple(kwargs.values()) + (record_id,)
        print(columns, values)
        query = f"UPDATE {self.table_name} SET {columns} WHERE id = %s"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query, values)
            self.mysql.connection.commit()
            cursor.close()
            return {"status": "success", "message": "Update success"}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # get all
    def get(self):
        """get all of data"""
        query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in result]
            cursor.close()
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # delete
    def delete(self, id):
        """Delete a record by id."""
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query, (id,))
            self.mysql.connection.commit()
            cursor.close()
            return {"status": "success", "message": "Delete success"}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # get first row
    def first(self):
        """Get the first row in the table."""
        query = f"SELECT * FROM {self.table_name} ORDER BY id ASC LIMIT 1"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query)
            record = cursor.fetchone()
            if record:
                columns = [desc[0] for desc in cursor.description]
                record = dict(zip(columns, record))
            cursor.close()
            if record:
                return {"status": "success", "data": record}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # where clause
    def where(self, **kwargs):
        """Get records based on specific conditions."""
        conditions = " AND ".join([f"{key} = %s" for key in kwargs.keys()])
        values = tuple(kwargs.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions} ORDER BY created_at DESC"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query, values)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in result]
            cursor.close()
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # whene value not not
    def notwhere(self, **kwargs):
        """Get records where specific conditions are not met."""
        conditions = " AND ".join([f"{key} != %s" for key in kwargs.keys()])
        values = tuple(kwargs.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions} ORDER BY created_at DESC"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query, values)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in result]
            cursor.close()
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": "Server error"}

    # get valid columns
    def _get_valid_columns(self):
        """Get valid columns for the table."""
        query = f"SHOW COLUMNS FROM {self.table_name}"
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute(query)
            columns = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return columns
        except Exception as e:
            return []

    # where clasuse count
    def count(self, **kwargs):
        try:
            if kwargs:
                valid_columns = self._get_valid_columns()
                for column in kwargs.keys():
                    if column not in valid_columns:
                        raise ValueError(f"Invalid column name: {column}")
                conditions = " AND ".join([f"`{key}` = %s" for key in kwargs.keys()])
                values = tuple(kwargs.values())
                query = f"SELECT COUNT(*) AS count FROM `{self.table_name}` WHERE {conditions}"
            else:
                query = f"SELECT COUNT(*) AS count FROM `{self.table_name}`"
                values = ()

            cursor = self.mysql.connection.cursor()
            cursor.execute(query, values)
            cursor.execute(query, values)
            result = cursor.fetchone()
            cursor.close()
            count = result["count"] if "count" in result else result[0]
            return {"status": "success", "data": count}
        except Exception as e:
            return {"status": "error", "message": str(e)}
