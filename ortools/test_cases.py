import assembly
#import machining
import unittest

#class TestAdd(unittest.TestCase):
##    def test_input_one_group(self):
##        self.assertTrue(assembly.test_one_groups())
#    #def test_input_multiple_group(self):
#    #    self.assertTrue(assembly.test_multiple_groups())
#    #def test_schedule_before(self):
#    #    self.assertTrue(assembly.test_schedule_before())
#    def test_schedule_feb15(self):
#        self.assertTrue(assembly.test_schedule_feb15())
class t76910(unittest.TestCase):
#    def test_input_one_group(self):
#        self.assertTrue(assembly.test_one_groups())
    #def test_input_multiple_group(self):
    #    self.assertTrue(assembly.test_multiple_groups())
    #def test_schedule_before(self):
    #    self.assertTrue(assembly.test_schedule_before())
    def test_76910(self):
        self.assertTrue(assembly.test_schedule_77356)
#class test_machine(unittest.TestCase):
#    def test_input(self):
#        self.assertTrue(machining.assembly_scheduling.read_data_excel('machine_input.xlsx','02.02.2019','Data'))
if __name__ == '__main__':
   #unittest.main() 
   #assembly.test_schedule_77356(73799)
   #assembly.test_schedule_feb11()
   #assembly.test_schedule_76910('Feb13.xlsx','13.02.2019','Production Meeting')
   #assembly.test_multiple_groups('KPI_file.xlsx','11.02.2019','Feb12')
   #assembly.test_multiple_groups('Assembly_input-one.xlsx','11.02.2019','Feb11')
   #assembly.test_schedule_76910('test/V3.xlsx','18.02.2019','Feb19')
   #assembly.test_schedule_76910('test/feb26.xlsx','26.02.2019','Production Meeting')  
   assembly.test_multiple_groups('test/bestfit.xlsx','18.02.2019','Sheet1')
  #assembly.test_schedule_76910('Feb15-v1.xlsx','15.02.2019','Production Meeting')
   #assembly.test_multiple_groups('Feb15-v1.xlsx','12.02.2019','Feb12')
   #assembly.test_multiple_groups('test1.xlsx','02.11.2019','test input')