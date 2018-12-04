import sqlite3

class BotDataManager():
    def __init__():
        create_main_data_table = """
        CREATE TABLE main_data (
        language VARCHAR(10) PRIMARY KEY
        start_message VARCHAR(50)
        about_message VARCHAR(1000)
        filter_news VARCHAR(30)
        filter_tutoring VARCHAR(30)
        filter_studygroups VARCHAR(20)
        filter_events VARCHAR(20)
        filter_about VARCHAR(20)
        );
        """
        connection = sqlite3.connect("botdata.db")
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS main_data")
        cursor.execute(create_main_data_table)
        connection.commit()
        connection.close()

        
