import sqlite3
from sqlite3 import Error
#  file to create database and tables
 
def create_connection(db_file):
  """ create a database connection to the SQLite database
      specified by db_file
  :param db_file: database file
  :return: Connection object or None
  """
  conn = None
  try:
    conn = sqlite3.connect(db_file)
    # print(sqlite3.version)
    return conn
  except Error as e:
    print(e)

  return conn
 
def create_table(conn, create_table_sql):
  """ create a table from the create_table_sql statement
  :param conn: Connection object
  :param create_table_sql: a CREATE TABLE statement
  :return:
  """
  try:
    c = conn.cursor()
    c.execute(create_table_sql)
  except Error as e:
    print(e)

def main(database):

  sql_create_teams_table = ''' CREATE TABLE IF NOT EXISTS teams (
                                  id integer PRIMARY KEY
                                    UNIQUE ON CONFLICT IGNORE,
                                  name text NOT NULL
                                    UNIQUE ON CONFLICT IGNORE,
                                  region text NOT NULL,
                                  seed integer NOT NULL,
                                  elo integer NOT NULL,
                                  pick_rate_1 real NOT NULL,
                                  pick_rate_2 real NOT NULL,
                                  pick_rate_3 real NOT NULL,
                                  pick_rate_4 real NOT NULL,
                                  pick_rate_5 real NOT NULL,
                                  pick_rate_6 real NOT NULL,
                                  pick_rate_7 real NOT NULL
                              );'''

  sql_create_users_table = ''' CREATE TABLE IF NOT EXISTS users (
                                    id integer PRIMARY KEY
                                      UNIQUE ON CONFLICT IGNORE,
                                    name text NOT NULL
                                      UNIQUE ON CONFLICT IGNORE
                                );'''

  team_array = []
  for i in range(1,69):

    team_array.append(",\n team_"+str(i)+"_wins integer")

  sql_create_entries_table = ''' CREATE TABLE IF NOT EXISTS entries (
                                    id integer PRIMARY KEY
                                      UNIQUE ON CONFLICT IGNORE,
                                    name text NOT NULL,
                                    espn_score integer,
                                    espn_percentile real,
                                    predicted_score_winner integer,
                                    predicted_score_loser integer'''+"".join(team_array)+'''
                                );'''

  sql_create_groups_table = ''' CREATE TABLE IF NOT EXISTS groups (
                                    id integer PRIMARY KEY
                                      UNIQUE ON CONFLICT IGNORE,
                                    name text NOT NULL
                                );'''

  sql_create_group_entries_table = ''' CREATE TABLE IF NOT EXISTS group_entries (
                                          id text PRIMARY KEY
                                            UNIQUE ON CONFLICT IGNORE,
                                          entry_id integer NOT NULL,
                                          group_id integer NOT NULL,
                                          FOREIGN KEY (entry_id) REFERENCES entries (id),
                                          FOREIGN KEY (group_id) REFERENCES groups (id)
                                      );'''

                                    
  sql_create_user_entries_table = ''' CREATE TABLE IF NOT EXISTS user_entries (
                                          id text PRIMARY KEY
                                            UNIQUE ON CONFLICT IGNORE,
                                          entry_id integer NOT NULL,
                                          user_id integer NOT NULL,
                                          FOREIGN KEY (entry_id) REFERENCES entries (id),
                                          FOREIGN KEY (user_id) REFERENCES users (id)
                                      );'''

  sql_create_picks_table = ''' CREATE TABLE IF NOT EXISTS picks (
                                  id text PRIMARY KEY
                                    UNIQUE ON CONFLICT IGNORE,
                                  entry_id integer NOT NULL,
                                  team_id integer NOT NULL,
                                  wins integer NOT NULL,
                                  FOREIGN KEY (entry_id) REFERENCES entries (id),
                                  FOREIGN KEY (team_id) REFERENCES teams (id)
                              );'''

 
  # create a database connection
  conn = create_connection(database)
 
    # create tables
  if conn is not None:
        # create projects table
    create_table(conn, sql_create_teams_table)
    create_table(conn, sql_create_entries_table)
    create_table(conn, sql_create_groups_table)
    create_table(conn, sql_create_group_entries_table)
    create_table(conn, sql_create_picks_table)
    create_table(conn, sql_create_users_table)
    create_table(conn, sql_create_user_entries_table)
  else:
    print("Error! cannot create the database connection.")
 
if __name__ == '__main__':
  main("db/m2019.db")
