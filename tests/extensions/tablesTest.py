# -*- coding: utf-8 -*-
#
# SqlPuzzle
# Michal Horejsek <horejsekmichal@gmail.com>
# https://github.com/horejsek/sqlPuzzle
#

import unittest

import sqlPuzzle.extensions.tables
import sqlPuzzle.joinTypes


class TablesTest(unittest.TestCase):
    def setUp(self):
        self.tables = sqlPuzzle.extensions.tables.Tables()

    def tearDown(self):
        self.tables = sqlPuzzle.extensions.tables.Tables()
    
    def testSimple(self):
        self.tables.set('table')
        self.assertEqual(str(self.tables), '`table`')
    
    def testSimpleAs(self):
        self.tables.set(('table', 't1'))
        self.assertEqual(str(self.tables), '`table` AS `t1`')
    
    def testMoreTables(self):
        self.tables.set('user', 'country')
        self.assertEqual(str(self.tables), '`user`, `country`')
    
    def testMoreTablesWithAs(self):
        self.tables.set(('user', 'u'), ('country', 'c'))
        self.assertEqual(str(self.tables), '`user` AS `u`, `country` AS `c`')
    
    def testSimpleInnerJoin(self):
        self.tables.set('user').innerJoin('country').on('user.country_id', 'country.id')
        self.assertEqual(str(self.tables), '`user` JOIN `country` ON (`user`.`country_id` = `country`.`id`)')
    
    def testSimpleAsInnerJoin(self):
        self.tables.set(('user', 'u')).innerJoin(('country', 'c')).on('u.country_id', 'c.id')
        self.assertEqual(str(self.tables), '`user` AS `u` JOIN `country` AS `c` ON (`u`.`country_id` = `c`.`id`)')
    
    def testSimpleMoreInnerJoins(self):
        self.tables.set('user')
        self.tables.innerJoin('country').on('user.country_id', 'country.id')
        self.tables.innerJoin('role').on('user.role_id', 'role.id')
        self.assertEqual(str(self.tables), '`user` JOIN `country` ON (`user`.`country_id` = `country`.`id`) JOIN `role` ON (`user`.`role_id` = `role`.`id`)')
    
    def testLeftJoin(self):
        self.tables.set('user')
        self.tables.leftJoin(('user', 'parent')).on('user.parent_id', 'parent.id')
        self.assertEqual(str(self.tables), '`user` LEFT JOIN `user` AS `parent` ON (`user`.`parent_id` = `parent`.`id`)')
    
    def testRightJoin(self):
        self.tables.set('t1')
        self.tables.rightJoin('t2').on('t1.id', 't2.id')
        self.assertEqual(str(self.tables), '`t1` RIGHT JOIN `t2` ON (`t1`.`id` = `t2`.`id`)')
    
    def testLeftAndInnerIsInner(self):
        self.tables.set('t1')
        self.tables.leftJoin('t2').on('t1.id', 't2.id')
        self.tables.join('t2').on('t1.id', 't2.id')
        self.assertEqual(str(self.tables), '`t1` JOIN `t2` ON (`t1`.`id` = `t2`.`id`)')
    
    def testIsSet(self):
        self.assertEqual(self.tables.isSet(), False)
        self.tables.set('table')
        self.assertEqual(self.tables.isSet(), True)
    
    def testIsSimple(self):
        self.tables.set('table')
        self.assertEqual(self.tables.isSimple(), True)
        self.tables.join('table2').on('id', 'id2')
        self.assertEqual(self.tables.isSimple(), False)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TablesTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

