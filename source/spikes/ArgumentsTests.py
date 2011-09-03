__author__ = 'Owner'

import unittest
from Arguments import *
#from Experiment import GreeterOverloaded

class MyTestCase(unittest.TestCase):
    def test_default_greeting_set(self):
        greeter = Greeter()
        self.assertEqual(greeter.message, 'Hello world!')

class GreeterTest(unittest.TestCase):
    def test_greetingReturnsDefault(self):
        mw = GreeterOverloaded()
        self.assertEqual(mw.greeting(),'Hello World!','greeting is not as expected')

    def test_greetingReturnsConstructorProvidedContent(self):
        mw = GreeterOverloaded('booyah!')
        self.assertEqual(mw.greeting(),'booyah!')

    def test_greetingReturnsConstructorProvidedContentArgsDemo(self):
        myArgument = {'arrrrr'}
        mw = GreeterOverloaded(*myArgument)
        self.assertEqual(mw.greeting(),'arrrrr')

class GreeterOverloadedWithOrTest(unittest.TestCase):
    def test_greetingReturnsDefault(self):
        mw = GreeterOverloadedWithOr()
        self.assertEqual(mw.greeting(),'Zoom!','greeting is not as expected')

    def test_greetingReturnsConstructorProvidedContent(self):
        mw = GreeterOverloadedWithOr('Yeah')
        self.assertEqual(mw.greeting(),'Yeah')

class GreeterOverloadedWithVariableArgsTest(unittest.TestCase):
    def test_greetingReturnsDefault(self):
        mw = GreeterOverloadedWithVariableArgs()
        self.assertEqual(mw.greeting(),'meh')

    def test_greetingReturnsConstructorProvidedContent(self):
        mw = GreeterOverloadedWithVariableArgs('Hello','beautiful','world')
        self.assertEqual(mw.greeting(),'Hello beautiful world')

class GreeterOverloadedWithKeywordArgsTest(unittest.TestCase):
    def test_greetingReturnsDefault(self):
        mw = GreeterOverloadedWithKeywordArgs()
        self.assertEqual(mw.greeting(),'Have a nice day!')

    def test_greetingReturnsKeywordArgsProvidedContent(self):
        mw = GreeterOverloadedWithKeywordArgs(part1='One ', part2='two')
        self.assertEqual(mw.greeting(),'One two')

    def test_greetingReturnsKeywordArgsProvidedContentDemo(self):
        myArguments = {'part1':'Good ', 'part2':'Luck!'}
        mw = GreeterOverloadedWithKeywordArgs(**myArguments)
        self.assertEqual(mw.greeting(),'Good Luck!')

if __name__ == '__main__':
    unittest.main()
