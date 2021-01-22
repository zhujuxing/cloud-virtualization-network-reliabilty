from NetEvoRulAna import *
import os
import time


def vSwitchTest():
    print('----------vSwitchTest----------')
    t1 = time.time()
    gName = CloudVritualizedNetwork(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx')
    evolName = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep + 'RulAnaTestFile'+os.sep+'evol_Rule_VswitchFail.xlsx'
    g_t = testRulAna(gName, evolName)
    printLog()
    t2 = time.time()
    print(g_t, '\n')
    print('Total time spent: ', round(t2 - t1, 4), 's\n', sep='')

def hardwareTest():
    print('----------HardWareTest----------')
    t1 = time.time()
    gName = CloudVritualizedNetwork(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx')
    evolName = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep + 'RulAnaTestFile'+os.sep+'evol_Rule_HardwareFail.xlsx'
    g_t = testRulAna(gName, evolName)
    printLog()
    t2 = time.time()
    print(g_t, '\n')
    print('Total time spent: ', round(t2 - t1, 4), 's\n', sep='')

if __name__ == '__main__':
    vSwitchTest()
    hardwareTest()


