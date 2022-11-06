import mysql.connector
import sqlite3
import helper

class SqlConnexion:
    __instance = None
    
    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = SqlConnexion()
        return cls.__instance
    
    @classmethod
    def drop_instance(cls):
        if cls.__instance is not None:
            cls.__instance = None
    
    @classmethod
    def get_database_version(cls, database, xbmcMajorVersion):
        #see: https://kodi.wiki/view/Databases#Database_Versions
        if database == "video":
            if xbmcMajorVersion < 10: return 0
            elif xbmcMajorVersion == 10: return 37
            elif xbmcMajorVersion == 11: return 60
            elif xbmcMajorVersion == 12: return 75
            elif xbmcMajorVersion == 13: return 78
            elif xbmcMajorVersion == 14: return 90
            elif xbmcMajorVersion == 15: return 93
            elif xbmcMajorVersion == 16: return 99
            elif xbmcMajorVersion == 17: return 107
            elif xbmcMajorVersion == 18: return 116
            elif xbmcMajorVersion == 19: return 119
            else: return 120
        else: return 0
    
    def __init__(self):
        if SqlConnexion.__instance is not None:
            raise Exception("Use SqlConnexion.get_instance() singleton")
        
        self.__mysqlVideoConnection = None
        self.__sqliteVideoConnection = None
        
        self.videoDbType = ""
        self.musicDbType = ""
        
        majorversion = helper.get_xbmc_major_version()
        videodbversion = SqlConnexion.get_database_version("video", majorversion)
        
        xml = helper.load_xml("special://masterprofile/advancedsettings.xml")
        if xml:
            advancedsettingsxml = xml.getElementsByTagName('advancedsettings')
            advancedsettingsnode = advancedsettingsxml[0] if advancedsettingsxml and len(advancedsettingsxml)>0 else None
            if advancedsettingsnode:
                videodatabasexml = advancedsettingsnode.getElementsByTagName('videodatabase')
                videodatabasenode = videodatabasexml[0] if videodatabasexml and len(videodatabasexml)>0 else None
                if videodatabasenode:
                    dbtype = videodatabasenode.getElementsByTagName('type')[0].firstChild.nodeValue
                    if dbtype == "mysql":
                        dbhost = videodatabasenode.getElementsByTagName('host')[0].firstChild.nodeValue
                        dbport = videodatabasenode.getElementsByTagName('port')[0].firstChild.nodeValue #optional defaults to 3306
                        dbuser = videodatabasenode.getElementsByTagName('user')[0].firstChild.nodeValue
                        dbpass = videodatabasenode.getElementsByTagName('pass')[0].firstChild.nodeValue
                        dbname = videodatabasenode.getElementsByTagName('name')[0].firstChild.nodeValue #optional defaults to MyVideos
                        self.videoDbType = dbtype
                        self.__mysqlVideoConnection = mysql.connector.connect(
                          host=dbhost,
                          port=dbport,
                          user=dbuser,
                          password=dbpass,
                          database=("%s%s" %(dbname, str(videodbversion))),
                          charset="utf8",
                          autocommit=True
                        )
                    if dbtype == "sqlite3":
                        dbhost = videodatabasenode.getElementsByTagName('host')[0].firstChild.nodeValue
                        dbname = videodatabasenode.getElementsByTagName('name')[0].firstChild.nodeValue #optional defaults to MyVideos
                        self.videoDbType = dbtype
                        self.__sqliteVideoConnection = sqlite3.connect(helper.get_real_path("%s%s%s.db" %(dbhost, dbname, str(videodbversion))))
        
        if not self.__mysqlVideoConnection and not self.__sqliteVideoConnection:
            self.videoDbType = "sqlite3"
            self.__sqliteVideoConnection = sqlite3.connect(helper.get_real_path("special://masterprofile/Database/MyVideos%s.db" %str(videodbversion)))
    
    def __del__(self):
        if self.__mysqlVideoConnection:
            self.__mysqlVideoConnection.close()
            self.__mysqlVideoConnection = None
        if self.__sqliteVideoConnection:
            self.__sqliteVideoConnection.close()
            self.__sqliteVideoConnection = None
    
    def execute_sql_select(self, request):
        connexion = self.__mysqlVideoConnection if self.__mysqlVideoConnection else self.__sqliteVideoConnection
        if not connexion:
            raise Exception("Connexxion has been closed")
        cursor = connexion.cursor()
        cursor.execute(request)
        columns = cursor.description
        response = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        return response
