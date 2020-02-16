class TestClass:
    id = 21
    def __init__(self):
        print("class init")
        # self.id = 1

    def __del__(self):
        print("class del")

    def test(self):
        self.testcase1()

    def test2(self):
        print("test 2")

    @staticmethod
    def testcase1():
        print('test case1')

    def testcase2(self):
        self.test2()
        print("self id", self.id)

tclass = TestClass()
tclass.test()
tclass.testcase1()
tclass.testcase2()
TestClass.testcase1()
TestClass.test()

a = 'kkkk/kjkj'
print(a.replace('/', '-'))