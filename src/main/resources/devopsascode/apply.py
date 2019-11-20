#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import json
from overtherepy import LocalConnectionOptions, OverthereHost, OverthereHostSession
from com.xebialabs.overthere import OperatingSystemFamily

import sys

class XLRunner:

    def __init__(self,xlpath,server):
        self.xlpath = xlpath
        self.server = server
        self.session = None

    def get_xl_command(self):        
        options = '--xl-deploy-url {0} --xl-deploy-username {1} --xl-deploy-password {2}'.format(self.server['url'], self.server['username'],self.server['password'])        
        xl = "{0}/xl {1}".format(self.xlpath, options)        
        return xl 

    def parameters(self,content,values):        
        uploaded_file = self.session.upload_text_content_to_work_dir(content,"content.yaml")
        parameters = " -f "+uploaded_file.getPath()

        if len(values) > 0:
            parameters = parameters + " --values " + ",".join([ "{0}={1}".format(k,v) for k,v in values.items()])
              
        return parameters

    def command_line(self,content,values):        
        return "{0} apply {1}".format(self.get_xl_command(),self.parameters(content,values))

    def apply(self,content,values):       
        try:
            localOpts = LocalConnectionOptions(os=OperatingSystemFamily.UNIX)
            host = OverthereHost(localOpts)
            self.session =  OverthereHostSession(host,stream_command_output=False)
            command_line = self.command_line(content,values)
            #print command_line
            uploaded_runner = self.session.upload_text_content_to_work_dir(command_line,'xldeploy_xl_runner.sh',executable=True)
            #print uploaded_runner.path
            response = self.session.execute(command_line,check_success=False)
            print "\n```"
            print "\n ".join(response.stdout)
            print "\n ".join(response.stderr)
            print "```\n    "
            rc = response.rc
            if response.rc > 0:
                sys.exit(rc)
        finally:
            if not self.session==None:
                self.session.close_conn()

  
XLRunner("/tmp/client",server).apply(content, values)
