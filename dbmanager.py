import firebirdsql
import os



class DBConnection:
    def __init__(self,dbname=None):

        if os.path.exists(dbname):
            try:
                self.con = firebirdsql.connect(database = dbname, user = 'SYSDBA', password = 'masterke')
                self.cur = self.con.cursor()


            except:
                self.con = None
                self.cur=None

        else:
            self.con = None




    def __del__(self):
        self.cur.close()
        self.con.close()

    def getData(self,layer=None,name=None,column=None):
        times = []
        data = []
        try:
            if layer=="haltungen":
                self.cur.execute("Select zeitpunkt,{} from lau_gl_el where kante='{}'"" order by zeitpunkt;".format(column,name))
            else:
                self.cur.execute("Select zeitpunkt,{} from lau_gl_s where knoten='{}' order by zeitpunkt;".format(column, name))



            for entry in self.cur.fetchall():
                times.append(entry[0])
                data.append(entry[1])

            return times,data
        except:
            return [],[]

    def sql(self,sql):
        self.cur.execute(sql)
        return self.cur.fetchall()


    def getSpaltenNamen(self,table):
        self.cur.execute("select rdb$field_name from rdb$relation_fields where rdb$relation_name='{}';".format(str(table).upper()))
        return self.cur.fetchall()




