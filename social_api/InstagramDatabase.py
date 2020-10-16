import psycopg2

class InstagramDatabase(object):
    # create tables

    def create_table_inst(self):
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")

            cursor = connection.cursor()
            create_table_query = '''CREATE TABLE inst_tables
                  (us_id REAL PRIMARY KEY     NOT NULL,
                  inst_id    TEXT    NOT NULL,
                  table_name           TEXT    NOT NULL); '''

            cursor.execute(create_table_query)
            connection.commit()
            print("Table created successfully in PostgreSQL ")

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while creating PostgreSQL table", error)
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

    # methods to add inst friends of user by link
    def add_user_to_inst_db(self, us_id, inst_us_id):
        name = None
        is_contains = None
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")
            cursor = connection.cursor()

            name = '{}_{}_{}'.format('inst', us_id, inst_us_id)

            if (self.check_id_inst_tables(us_id, inst_us_id) == 0):
                postgres_insert_query = """ INSERT INTO inst_tables (us_id, inst_id, table_name) VALUES (%s, %s, %s)"""

                record_to_insert = (us_id, inst_us_id, name)
                cursor.execute(postgres_insert_query, record_to_insert)

                connection.commit()
                count = cursor.rowcount
                print(count, "Record inserted successfully into inst_tables table")
                is_contains = False
            else:
                is_contains = True


        except (Exception, psycopg2.Error) as error:
            if (connection):
                is_contains = True
                print("Failed to insert record into inst_tables table", error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
            print("PostgreSQL connection is closed")
            return name, is_contains

    #
    def create_table_friends_inst(self, name):
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")
            cursor = connection.cursor()

            create_table_query = '''CREATE TABLE {}
                  (ID SERIAL PRIMARY KEY     NOT NULL,
                  friend_id    TEXT    NOT NULL); '''.format(name)

            cursor.execute(create_table_query)
            connection.commit()
            print("Table created successfully in PostgreSQL ")

        except (Exception, psycopg2.Error) as error:
            if (connection):
                print("Failed to insert record into {} table".format(name), error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
            print("PostgreSQL connection is closed")

    #
    def check_id_inst_tables(self, user_id, inst_id):
        count = 0
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")
            cursor = connection.cursor()

            postgres_insert_query = """SELECT inst_id FROM inst_tables WHERE inst_id = '{}' and us_id = '{}'""".format(
                inst_id, user_id)

            cursor.execute(postgres_insert_query)

            connection.commit()
            count = cursor.rowcount
            print(count)

        except (Exception, psycopg2.Error) as error:
            if (connection):
                print("Failed command into inst_tables table", error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
            print("PostgreSQL connection is closed")
            return count

    #
    def add_inst_user_to_db(self, us_id, inst_us_id, friends):
        name, is_contains = self.add_user_to_inst_db(us_id, inst_us_id)
        if (is_contains == False):
            self.create_table_friends_inst(name)
        self.add_friends_table_inst(name, friends, is_contains)

    #
    def add_friends_table_inst(self, name, friends, is_contains):
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")
            cursor = connection.cursor()
            if (is_contains == False):
                # print
                postgres_insert_query = """ INSERT INTO {} (friend_id) VALUES """.format(name)

                for i in range(len(friends) - 1):
                    postgres_insert_query = postgres_insert_query + '({}), '.format(friends[i])

                postgres_insert_query = postgres_insert_query + '({});'.format(friends[i])
            else:
                postgres_insert_query = """ DROP TABLE {};

                                            CREATE TABLE {} (ID SERIAL PRIMARY KEY     NOT NULL,
                                            friend_id    TEXT    NOT NULL);

                                             INSERT INTO {} (friend_id) VALUES """.format(name, name, name)

                for i in range(len(friends) - 1):
                    postgres_insert_query = postgres_insert_query + '({}), '.format(friends[i])

                postgres_insert_query = postgres_insert_query + '({});'.format(friends[i])

            cursor.execute(postgres_insert_query)

            connection.commit()
            count = cursor.rowcount
            print(count, "Record inserted successfully into {} table".format(name))

        except (Exception, psycopg2.Error) as error:
            if (connection):
                print("Failed to insert record into {} table".format(name), error)
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
            print("PostgreSQL connection is closed")

    # methods to get list of friends inst on website
    def get_friends_us_id_by_table_name(self, name):
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")

            cursor = connection.cursor()

            postgres_insert_query = """SELECT us_id FROM inst_tables JOIN {} ON inst_tables.inst_id = {}.friend_id""".format(
                name, name)

            cursor.execute(postgres_insert_query)
            connection.commit()

            records = cursor.fetchall()
            print("Successfully in PostgreSQL ")

            pr_fr_l = []
            for item in records:
                pr_fr_l.append(item[0])

            records = pr_fr_l

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while creating PostgreSQL table", error)
            records = None
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
                return records

    def get_table_name_by_user_id(self, us_id):
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")

            cursor = connection.cursor()

            postgres_insert_query = """SELECT table_name FROM inst_tables WHERE inst_tables.us_id = '{}'""".format(
                us_id)

            cursor.execute(postgres_insert_query)
            connection.commit()

            records = cursor.fetchall()


            #         print(records)
            print("{} Successfully in PostgreSQL ".format(postgres_insert_query))


        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while creating PostgreSQL table", error)
            return None
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
                if (len(records) == 0):
                    return None
                return records[0][0]

    def create_table_confidance_on_site(self, us_id):
        table_name = 'friends_on_site_{}'.format(us_id)
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")
            cursor = connection.cursor()

            create_table_query = '''CREATE TABLE {}
                  (FRIEND_ID SERIAL PRIMARY KEY     NOT NULL,
                  confidance    REAL   NOT NULL); '''.format(table_name)

            cursor.execute(create_table_query)
            connection.commit()
            print("Table {} created successfully in PostgreSQL ".format(table_name))

        except (Exception, psycopg2.Error) as error:
            if (connection):
                print("Failed to create {} table".format(table_name), error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
            print("PostgreSQL connection is closed")

    def check_user_in_confidence_list(self, us_id, fr_id):
        count = 0
        is_contains_table = None
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")
            cursor = connection.cursor()

            postgres_insert_query = """SELECT FRIEND_ID FROM friends_on_site_{} WHERE FRIEND_ID = {}""".format(
                us_id, fr_id)

            cursor.execute(postgres_insert_query)

            connection.commit()
            count = cursor.rowcount
            print(count)
            is_contains_table = True
        except (Exception, psycopg2.Error) as error:
            if (connection):
                print("Failed command into friends_on_site_{} table".format(us_id), error)
                is_contains_table = False
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
            print("PostgreSQL connection is closed")
            return count, is_contains_table

    def check_users_in_confidence_list(self, friends_ids, us_id):
        proposed_friends_list = []
        for friend in friends_ids:
            is_contains = False
            while (is_contains == False):
                count, is_contains = self.check_user_in_confidence_list(us_id, friend)
                if (is_contains == False):
                    self.create_table_confidance_on_site(us_id)
            if (count == 0):
                proposed_friends_list.append(friend)
        return proposed_friends_list

    def push_notifications(self, us_id, friends):
        push_list = []
        for friend in friends:
            new_friend = self.check_users_in_confidence_list([us_id], friend)
            if (len(new_friend) == 1):
                push_list.append(friend)

        return push_list, us_id

    def get_view_proposed_fr_list(self, friend_list):
        #     method for web programmer. This method get list of friends id, which need to show
        return 0

    def update_mark_score_for_friend(self, us_id, friend_id, score):
        is_contains_table = None
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")
            cursor = connection.cursor()

            postgres_insert_query = """ UPDATE friends_on_site_{} SET confidance = {} WHERE friend_id = {}""".format(
                us_id, score, friend_id)

            cursor.execute(postgres_insert_query)

            connection.commit()
            count = cursor.rowcount
            print(count, "Record updated successfully into friends_on_site_{} table".format(us_id))

        except (Exception, psycopg2.Error) as error:
            if (connection):
                print("Failed command into {}_friends_on_site table".format(us_id), error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
            print("PostgreSQL connection is closed")
            return count

    def insert_mark_score_for_friend(self, us_id, friend_id, score):
        is_contains = None
        try:
            connection = psycopg2.connect(dbname="",
                                          user="",
                                          password="",
                                          host="",
                                          port="")

            cursor = connection.cursor()

            postgres_insert_query = """ INSERT INTO friends_on_site_{} (friend_id, confidance) VALUES ({}, {})""".format(
                us_id, friend_id, score)

            cursor.execute(postgres_insert_query)
            connection.commit()

            records = cursor.fetchall()
            #         print(records)
            print("Successfully in PostgreSQL ")
            is_contains = False

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error request: {}.     ".format(postgres_insert_query), error)
            is_contains = True
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
                return is_contains