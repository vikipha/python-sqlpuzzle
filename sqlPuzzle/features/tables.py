# -*- coding: utf-8 -*-
#
# SqlPuzzle
# Michal Horejsek <horejsekmichal@gmail.com>
# https://github.com/horejsek/sqlPuzzle
#

import sqlPuzzle.argsParser
import sqlPuzzle.features.conditions
import sqlPuzzle.joinTypes
import sqlPuzzle.sqlValue



class OnCondition(sqlPuzzle.features.conditions.Condition):
    def __str__(self):
        """
        Print part of query.
        """
        return '%s = %s' % (
            sqlPuzzle.sqlValue.SqlReference(self._column),
            sqlPuzzle.sqlValue.SqlReference(self._value),
        )
    
    def __repr__(self):
        return "<OnCondition: %s>" % self.__str__()
    
    def __eq__(self, other):
        """
        Are on codntions equivalent?
        """
        return (
            (self._column == other._column and self._value == other._value) or
            (self._column == other._value and self._value == other._column)
        )



class Ons(sqlPuzzle.features.conditions.Conditions):
    def __init__(self):
        """
        Initialization of Ons.
        """
        super(Ons, self).__init__(OnCondition)
    
    def __str__(self):
        """
        Print part of query.
        """
        if self.isSet():
            return " AND ".join(str(condition) for condition in self._conditions)
        return ""
    
    def __repr__(self):
        return "<Ons: %s>" % self.__str__()



class Table(object):
    def __init__(self, table=None, as_=None):
        """
        Initialization of Table.
        """
        self.table(table)
        self.as_(as_)
        
        self._joins = []
    
    def __str__(self):
        """
        Print part of query.
        """
        if self._as:
            table = '%s AS %s' % (
                sqlPuzzle.sqlValue.SqlReference(self._table),
                sqlPuzzle.sqlValue.SqlReference(self._as),
            )
        else:
            table = str(sqlPuzzle.sqlValue.SqlReference(self._table))
        
        if self._joins != []:
            if any([not join['ons'].isSet() for join in self._joins]):
                raise sqlPuzzle.exceptions.InvalidQueryException("You can't use join without on.")
            
            self.__minimizeJoins()
            table = '%s %s' % (
                table,
                ' '.join([
                    '%s %s ON (%s)' % (
                        sqlPuzzle.joinTypes.JOIN_TYPES[join['type']],
                        str(join['table']),
                        str(join['ons']),
                    ) for join in self._joins
                ])
            )
        
        return table
    
    def __repr__(self):
        return "<Table: %s>" % self.__str__()
    
    def __eq__(self, other):
        """
        Are tables equivalent?
        """
        return (
            self._table == other._table and
            self._as == other._as and
            self._joins == other._joins
        )
    
    def __minimizeJoins(self):
        """
        Minimize of joins.
        Left/right and inner join of the same join is only inner join.
        """
        joinsGroup = []
        for join in self._joins:
            appendNew = True
            for joinGroup in joinsGroup:
                if joinGroup[0]['table'] == join['table'] and joinGroup[0]['ons'] == join['ons']:
                    joinGroup.append(join)
                    appendNew = False
                    break
            if appendNew:
                joinsGroup.append([join])
        
        self._joins = []
        for joins in joinsGroup:
            if len(joins) > 1 and any(bool(join['type'] == sqlPuzzle.joinTypes.INNER_JOIN) for join in joins):
                joins[0]['type'] = sqlPuzzle.joinTypes.INNER_JOIN
                self._joins.append(joins[0])
            else:
                self._joins.extend(joins)
        
    def isSimple(self):
        """
        Is set table without join?
        """
        return self._joins == []
    
    def table(self, table):
        """
        Set table.
        """
        self._table = table
    
    def as_(self, as_):
        """
        Set as.
        """
        self._as = as_
    
    def join(self, arg, joinType=sqlPuzzle.joinTypes.INNER_JOIN):
        """
        Join table.
        """
        if isinstance(arg, (list, tuple)) and len(arg) == 2:
            table = Table(*arg)
        else:
            table = Table(arg)
        
        self._joins.append({
            'type': joinType,
            'table': table,
            'ons': Ons(),
        })
    
    def on(self, *args, **kwds):
        """
        Join on.
        """
        if self.isSimple():
            raise sqlPuzzle.exceptions.InvalidQueryException("You can't set join without table.")
        
        self._joins[-1]['ons'].where(*args, **kwds)



class Tables(object):
    def __init__(self):
        """
        Initialization of Tables.
        """
        self._tables = []
    
    def __str__(self):
        """
        Print tables (part of query).
        """
        return ", ".join(str(table) for table in self._tables)
    
    def __repr__(self):
        return "<Tables: %s>" % self.__str__()
    
    def __contains__(self, item):
        """
        Is item (table) in list of tables?
        """
        for table in self._tables:
            if item == table:
                return True
        return False
    
    def isSet(self):
        """
        Is tables set?
        """
        return self._tables != []
    
    def isSimple(self):
        """
        Is set only one table without join?
        """
        return len(self._tables) == 1 and self._tables[0].isSimple()
    
    def set(self, *args):
        """
        Set tables.
        """
        args = [arg for arg in args if arg]
        
        for table, as_ in sqlPuzzle.argsParser.parseArgsToListOfTuples(
            {'maxItems': 2, 'allowedDataTypes': ((str, unicode, sqlPuzzle.queries.select.Select), (str, unicode))}, *args
        ):
            table = Table(table, as_)
            if table not in self:
                self._tables.append(table)
        
        return self
    
    def join(self, arg):
        """
        Join table.
        """
        if not self.isSet():
            raise sqlPuzzle.exceptions.InvalidQueryException("You can't set join without table.")
        
        self._tables[-1].join(arg, sqlPuzzle.joinTypes.INNER_JOIN)
        return self
    
    def innerJoin(self, arg):
        """
        Inner join table.
        """
        if not self.isSet():
            raise sqlPuzzle.exceptions.InvalidQueryException("You can't set join without table.")
        
        self._tables[-1].join(arg, sqlPuzzle.joinTypes.INNER_JOIN)
        return self
    
    def leftJoin(self, arg):
        """
        Left join table.
        """
        if not self.isSet():
            raise sqlPuzzle.exceptions.InvalidQueryException("You can't set join without table.")
        
        self._tables[-1].join(arg, sqlPuzzle.joinTypes.LEFT_JOIN)
        return self
    
    def rightJoin(self, arg):
        """
        Right join table.
        """
        if not self.isSet():
            raise sqlPuzzle.exceptions.InvalidQueryException("You can't set join without table.")
        
        self._tables[-1].join(arg, sqlPuzzle.joinTypes.RIGHT_JOIN)
        return self
    
    def on(self, *args, **kwds):
        """
        Join on.
        """
        if not self.isSet():
            raise sqlPuzzle.exceptions.InvalidQueryException("You can't set condition of join without table.")
        
        self._tables[-1].on(*args, **kwds)
        return self

