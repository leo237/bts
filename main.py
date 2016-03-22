import tornado.web
import tornado.httpserver
import tornado.options
import tornado.ioloop
import tornado.websocket
import os.path
import re
import json
#---------------------------------------------------------------------------

from tornado.options import define, options, parse_command_line

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class SanitizeHandler (tornado.web.RequestHandler):
    def get(self):
        self.render('sanitize.html')


class DiffCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('diffchecker.html')



#------------------------WEB SOCKET HANDLER-----------------------------
class WSHandler(tornado.websocket.WebSocketHandler):
     
    def open(self):
        pass
        # print("socket opened server side")
            
    def on_message(self, message):
        messageFromClient = json.loads(message)
        messageType = str(messageFromClient['messageType'])
        if messageType == "sanitize":
            pattern = messageFromClient['pattern']
            text = messageFromClient['leftTextArea']
            print pattern
            textList = text.split('\n')
            print textList

            sanitized = []
            for each in textList:
                regex = re.search(pattern, each)
                if regex:
                    found = regex.group(0)
                    print found
                    sanitized.append(found)

            dataDict = {'messageType':'sanityResult','result':sanitized}
            messageToClient = json.dumps(dataDict)
            self.write_message(messageToClient) 

        elif messageType == "finddiff":
            original = messageFromClient['original']
            toFind = messageFromClient['toFind']
            originalList = original.split('\n')
            notFound = []
            for each in originalList:
                if not re.search(r".*" + re.escape(each) + r".*", toFind):
                    notFound.append(each)
            dataDict = {'messageType':'diffResult', 'result':notFound}
            messageToClient = json.dumps(dataDict)
            self.write_message(messageToClient)
    def on_close(self):
        pass
        # print("Socket closed server side")

        
handlers = [
    (r'/',IndexHandler),
    (r'/sanitize', SanitizeHandler),
    (r'/diffChecker', DiffCheckHandler),
    (r'/ws',WSHandler),
]

#---------------------------------------------------------------------------

if __name__ == "__main__":
    parse_command_line()
    # template path should be given here only unlike handlers
    app = tornado.web.Application(handlers, template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                  static_path=os.path.join(os.path.dirname(__file__), "static"), cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=", debug=True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888, address='0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()
