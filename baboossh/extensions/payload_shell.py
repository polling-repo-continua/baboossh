class ExtStr(type):
    def __str__(self):
        return self.getKey()

class BaboosshExt(object,metaclass=ExtStr):
    @classmethod
    def getModType(cls):
        return "payload"

    @classmethod
    def getKey(cls):
        return "shell"

    @classmethod
    def descr(cls):
        return "Get a shell on target"
    
    @classmethod
    def buildParser(cls,parser):
        pass

    @classmethod
    def run(cls,socket, connection,wspaceFolder, stmt):
        try:
            socket.run("sh",pty="vt100")
        except OSError as e:
            print(e.errno)
        except Exception as e:
            print("Error : "+str(e))
            return False
        return True
    
