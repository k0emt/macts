__author__ = 'Owner'

class Greeter:
    def __init__(self):
        self.message = 'Hello world!'
        # print self.message

class GreeterOverloaded:
    def __init__(self, greeting=None):
            if greeting is None:
                    self.myGreeting = 'Hello World!'
            else:
                    self.myGreeting = greeting

    def greeting(self):
            return self.myGreeting

class GreeterOverloadedWithOr:
    def __init__(self, greeting=None):
        self.myGreeting = greeting or 'Zoom!'

    def greeting(self):
            return self.myGreeting

class GreeterOverloadedWithVariableArgs:
    def __init__(self, *args ):
        self.myGreeting = 'meh'
        if len(args) > 0:
            self.myGreeting = ''
            for arg in args:
                self.myGreeting += arg + ' '
            self.myGreeting = self.myGreeting.strip()

    def greeting(self):
            return self.myGreeting

class GreeterOverloadedWithKeywordArgs:
    def __init__(self, **kwargs):
        self.myGreeting = 'Have a nice day!'
        if len(kwargs) > 0:
            self.myGreeting = kwargs['part1'] + kwargs['part2']

    def greeting(self):
            return self.myGreeting

# a good reference for getting and sending arguments can be found here:
# http://www.saltycrane.com/blog/2008/01/how-to-use-args-and-kwargs-in-python/
