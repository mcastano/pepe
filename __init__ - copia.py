#from yaml import load, dump
import json, os, requests, time, copy
def server():
    try:
        return os.environ['OLP_SERVER']
    except KeyError as error:
        raise KeyError('Variable no definida en el entorno ' + error.message)

def __directory__(fichero):
    xFichero =""
    if os.path.isfile(fichero):
        xFichero = os.getcwd()+os.sep+fichero
    elif os.path.isfile("."+os.sep+"templates"+os.sep + fichero):
        #os.chdir("." + os.sep + "templates" + os.sep)
        xFichero = os.getcwd() + os.sep + "templates" + os.sep + fichero
    else:
        dirActual = os.getcwd()
        os.chdir("..")
        if dirActual != os.getcwd():
            xFichero = __directory__(fichero)
        os.chdir(dirActual)
    return xFichero

class catalog:
    requests = {}

    def __init__(self, fichero1=""):
        if fichero1 != "":
            self.load(fichero1)

    def load(self, fichRequest):

        xFichero = __directory__(fichRequest)
        if xFichero == "":
            raise IOError("file " + fichRequest + " no found")
        f = open(xFichero)
        try:
            template = json.load(f) # Controlar error IndentationError
        except Exception  as error:
            raise Exception("Error JSON in file '" + xFichero + "' : " + error.message)

        if "__parent__" in template:
            self.parent = catalog()
            self.parent.load (template["__parent__"])

        self.requests = template
        f.close()

    def new (self, select):

        compose = {}
        if not select in self.requests:
                return
        check_all = {}
        check_template = {}
        check_compose = {}

        requests = self.requests

        if '__all__' in self.parent.requests:
            compose.update(self.parent.requests['__all__'])
            intermedio = self.parent.requests['__all__']
            if 'CHECK' in intermedio:
                check_all = copy.copy(intermedio['CHECK'])

        obj = requests[select]
        if '__template__' in requests[select]:
            compose.update(self.parent.requests[obj['__template__']])
            intermedio = self.parent.requests[obj['__template__']]
            if 'CHECK' in intermedio:
                check_template = copy.copy(intermedio['CHECK'])

        compose.update (obj)

        compose['CHECK'] = {}

        compose['CHECK'].update(check_all)
        compose['CHECK'].update(check_template)

        if 'CHECK' in obj:
            compose['CHECK'].update (obj['CHECK'])


        mobj = services()

        mobj.url = copy.copy(compose['URL'])
        mobj.verbo =  copy.copy(compose['VERBO'])
        mobj.headers = copy.copy(compose['HEADERS'])
        mobj.body = copy.copy(compose['BODY'])
        mobj.check = {}
        try:
            mobj.check = copy.copy(compose['CHECK'])
        except:
            pass

        return mobj

class services:
    url = {}
    verbo = {}
    headers = {}
    body ={}
    check = {}
    response = {}
    template = {}
    parameters_URL = {}
    parameters_BODY = {}
    parameters_HEADERS ={}
    queryString = {}
    parameters_FIELDS = {}
    parameters_FILTERS = {}

    def __init__ (self, fichero1="", fichero2=""):

        self.url = {}
        self.verbo = {}
        self.headers = {}
        self.body = {}
        self.check = {}
        self.response = {}
        self.template = {}
        self.parameters_URL = {}
        self.parameters_BODY = {}
        self.parameters_HEADERS = {}
        self.queryString = {}
        self.parameters_FIELDS = {}
        self.parameters_FILTERS = {}
        if fichero1 != "":
            self.load(fichero1, fichero2)

    def __directory__ (self, fichero):
        xFichero =""
        if os.path.isfile(fichero):
            xFichero = os.getcwd()+os.sep+fichero
        elif os.path.isfile("."+os.sep+"templates"+os.sep + fichero):
            #os.chdir("." + os.sep + "templates" + os.sep)
            xFichero = os.getcwd() + os.sep + "templates" + os.sep + fichero
        else:
            dirActual = os.getcwd()
            os.chdir("..")
            if dirActual != os.getcwd():
                xFichero = self.__directory__(fichero)
            os.chdir(dirActual)
        return xFichero

    def load (self, fichRequest, fichResponse=""):

        # mystring = mystring.replace('\n', ' ').replace('\r', '')
        #
        xFichero = self.__directory__(fichRequest)
        if xFichero=="":
            raise IOError ("file " + fichRequest + " no found")
        f = open(xFichero)
        template = json.load(f)

        self.url = template['URL']
        self.verbo  = template['VERBO']
        self.headers = template ['HEADERS']
        self.body = template['BODY']

        try:
            self.check = template['CHECK']
        except:
            pass

        self.template = template
        f.close()
        """
        if fichResponse =="":
            xFichero = self.__directory__(fichResponse)
            if xFichero == "":
                raise IOError("file " + fichResponse + " no found")
            f = open(xFichero)
            template = json.load(f)
            self.response = template
            f.close()
        """
    def parameterURL (self, parameter, value):
        self.parameters_URL[parameter] = value

    def query(self, parameter, value):
        self.queryString[parameter] = str(value)

    def fields(self, parameter):
        campo = parameter.split(",")
        for field in campo:
            self.parameters_FIELDS[field] = str(field).strip()

    def getFields (self):
        if len(self.parameters_FIELDS)==0:
            return ""

        listKey = list(self.parameters_FIELDS.keys())
        cadena = ""
        for key in listKey:
            cadena = cadena + self.parameters_FIELDS[key] + ","
        return "fields=" + cadena[:len(cadena)-1]

    def filters(self, field, condition="", value=""):
        condiciones = ['[EQ]', '[NEQ]', '[LT]', '[GT]', '[LTE]', '[GTE]', '[MATCH]' '[EXISTS]', '[ALL]', '[IN]',
                       '[NIN]']

        if (condition !=""):
            if (condition in condiciones):
                self.parameters_FILTERS[field + condition + value] = {"field": field, "condition": condition,
                                                                      "value": value}
        if (condition==""):

            for item in condiciones:
                if (field.find(item))>-1:
                    resultado = field.split(item)
                    field = resultado[0]
                    condition = item
                    value = resultado[1]
                    self.parameters_FILTERS[field + condition + value] = {"field": field, "condition": condition,
                                                                          "value": value}
                    break


        #str(field)+str(condition)+str(value)

    def getFiters(self):
        if len(self.parameters_FILTERS) == 0:
            return ""

        listKey = list(self.parameters_FILTERS.keys())
        cadena = ""
        for key, values in self.parameters_FILTERS.items():
            cadena = cadena + values['field'] + values['condition'] + values['value'] + ","
            #cadena = cadena + self.parameters_FILTERS[key] + ","
        return "filters="+cadena[:len(cadena) - 1]

    def getQuery (self):
        mFields = self.getFields()
        mFilters = self.getFiters()
        if len(self.queryString)==0 and len(mFields) ==0 and len(mFilters)==0:
            return ""
        final =""
        listKey = list(self.queryString.keys())
        cadena = ""
        for key in listKey:
            cadena = cadena + key + "=" + self.queryString[key] + "&"

        if len(self.queryString)<>0:
            cadena = cadena[:len(cadena)-1]

        if len(mFields) > 0:
            final = final + mFields + "&"
        if len(mFilters) > 0:
            final=final + mFilters + "&"
        if len(cadena) > 0:
            final = final+cadena + "&"

        final = "?" + final[:len(final)-1]

        return final

    def getURL (self):
        murl = self.url

        listKey = list(self.parameters_URL.keys())
        for key in listKey:
            murl = murl.replace ("{" + key +"}", str(self.parameters_URL[key]))

        return murl + self.getQuery()

    def send (self):
        # type: () -> object
        #self.verbo
        mUrl = self.getURL()
        if (self.verbo =="POST"):
            time1 = int(round(time.time() * 1000))
            r = requests.post(mUrl, json=self.body, headers=self.headers)
            time2 = int(round(time.time() * 1000))
        elif (self.verbo =="GET"):
            time1 = int(round(time.time() * 1000))
            r = requests.get(mUrl, headers=self.headers )
            time2 = int(round(time.time() * 1000))
        elif (self.verbo =="PUT"):
            time1 = int(round(time.time() * 1000))
            r = requests.put(mUrl, json=self.body, headers=self.headers)
            time2 = int(round(time.time() * 1000))
        elif (self.verbo =="DELETE"):
            time1 = int(round(time.time() * 1000))
            r = requests.delete(mUrl, headers=self.headers)
            time2 = int(round(time.time() * 1000))

        #self.response.raw = r
        self.response['raw'] = r
        self.response['code'] = r.status_code
        self.response['headers'] = r.headers
        self.response['time_milliseconds'] = time2 - time1
        if r.text !="":
            self.response['body'] = json.loads(r.text)

    def set (self, attr, data):
        campo = attr.split(".")
        intermedio = self.body
        anterior = self.body
        for atributo in campo:
            anterior = intermedio
            try:
                intermedio = intermedio[atributo]
            except:
                intermedio[atributo]=""

        anterior[atributo] = data

        #self.body[attr] = data

    def clear (self, value):
        self.__clearDic__(self.body, value)
        for item in self.parameters_FILTERS.keys():
            obj = self.parameters_FILTERS[item]
            if (obj['value']==value):
                del self.parameters_FILTERS[item]
        #self.__clearDic__(self.parameters_FILTERS, value)

    def __clearDic__ (self, objDic, value):
        intermedio = objDic
        anterior = objDic
        listaKey = list(objDic.keys())
        for campo in listaKey:
            if not type(intermedio[campo]) is dict:
                if (intermedio[campo]==value):
                    del anterior[campo]
            else:
                self.__clearDic__(intermedio[campo], value)
                if (len(intermedio[campo])==0):
                    del anterior[campo]

    def assert_code (self, code):
        resultado = str(self.response['code']).startswith(str(code))
        assert resultado, "Codigo esperado " + str(code) + " recibido " + str(self.response['code'])

    def assert_exist (self, attr):
        campo = attr.split(".")
        intermedio = self.response['body']
        anterior = self.response['body']
        for atributo in campo:
            anterior = intermedio
            try:
                intermedio = intermedio[atributo]
            except:
                assert False, "No se ha encontrado el atributo " + attr
        assert True
        #anterior[atributo] = data

    def assert_length(self, attr, Length):
        campo = attr.split(".")
        intermedio = self.response['body']
        anterior = self.response['body']
        for atributo in campo:
            anterior = intermedio
            try:
                intermedio = intermedio[atributo]
            except:
                assert False, "No se ha encontrado el atributo " + attr

        assert (len(anterior[atributo])== Length), "No contiene la longitud suficiente"

    def assert_value(self, attr, value):
        attr = attr.replace('[',".").replace(']',"")
        campo = attr.split(".")
        intermedio = self.response['body']
        anterior = self.response['body']
        for atributo in campo:
            lista = isinstance(intermedio, list)
            anterior = intermedio
            try:
                if lista:
                    intermedio = intermedio[int(atributo)]
                else:
                    intermedio = intermedio[atributo]
            except:
                assert False, "No se ha encontrado el atributo " + attr

        assert (str(anterior[atributo]).startswith(str(value))), "No coinciden los valores esperados entre " + str(anterior[atributo]) + " y " + str(value)

    def length (self, attr):
        campo = attr.split(".")
        intermedio = self.response['body']
        anterior = self.response['body']
        for atributo in campo:
            anterior = intermedio
            try:
                intermedio = intermedio[atributo]
            except:
                assert False, "No se ha encontrado el atributo " + attr
                return -1
        return (len(anterior[atributo]))

    def value (self, attr):
        campo = attr.split(".")
        intermedio = self.response['body']
        anterior = self.response['body']
        for atributo in campo:
            anterior = intermedio
            try:
                intermedio = intermedio[atributo]
            except:
                assert False, "No se ha encontrado el atributo " + attr
                return -1

        return (anterior[atributo])

    def assert_headers (self, attribute, valor=""):
        h = self.response['headers']
        result = h[attribute]
        if valor != "":
            result = (h[attribute].find (valor)>-1)

        if (attribute =="content-length"):
            result = long(result)
            return result
        else:
            return result

    def assert_response (self, selector):
        #h = self.response['headers']
        aCheck = list()
        sCheck = list()

        if "__all__" in self.check:
            aCheck = self.check['__all__']
        elif selector in self.check:
            sCheck = self.check[selector]

        mCheck = aCheck + sCheck

        if len(mCheck) == 0:
            return

        respuestaFinal = True
        respuestaString = "\n"
        contador = 1

        for item in mCheck:
            try:
                respuesta = eval(item[0])
            except Exception as error:
                respuesta = False

            if not respuesta:
                respuestaString = respuestaString + "("+str(contador)+") "+ item[1] + ". [" + item[0]+ "]\n"
                contador = contador + 1
            if respuestaFinal:
                respuestaFinal = respuesta

        assert respuestaFinal, respuestaString

    def printRequest (self):

        print ("REQUEST")
        print ("*******")
        print ("url")
        print ("---")
        print self.getURL()
        print ("headers")
        print ("-------")
        print json.dumps(self.headers, indent=3)
        print ("body")
        print ("----")
        print json.dumps(self.body, indent=3)

    def printResponse (self):

        print ("RESPONSE")
        print ("*******")
        print ("url")
        print ("---")
        print self.getURL()
        print ("code")
        print ("-------")
        print self.response['code']
        print ("headers")
        print ("-------")
        print json.dumps(str(self.response['headers']), indent=3)
        print ("body")
        print ("----")
        if "body" in self.response:
            print json.dumps(self.response['body'], indent=3)
        else:
            print ("--VACIO--")