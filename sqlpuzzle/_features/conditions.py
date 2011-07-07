# -*- coding: utf-8 -*-
#
# sqlpuzzle
# Michal Horejsek <horejsekmichal@gmail.com>
# https://github.com/horejsek/sqlpuzzle
#

import datetime

import sqlpuzzle._libs.argsParser
import sqlpuzzle._libs.sqlValue
import sqlpuzzle.exceptions
import sqlpuzzle.relations


class Condition(sqlpuzzle._features.Feature):
    __defaultRelations = {
        str: sqlpuzzle.relations.EQ,
        unicode: sqlpuzzle.relations.EQ,
        int: sqlpuzzle.relations.EQ,
        long: sqlpuzzle.relations.EQ,
        float: sqlpuzzle.relations.EQ,
        bool: sqlpuzzle.relations.EQ,
        list: sqlpuzzle.relations.IN,
        tuple: sqlpuzzle.relations.IN,
        datetime.date: sqlpuzzle.relations.EQ,
        datetime.datetime: sqlpuzzle.relations.EQ,
    }
    
    def __init__(self):
        """Initialization of Condition."""
        self._column = None
        self._value = None
        self._relation = None
    
    def __str__(self):
        """Print condition (part of WHERE)."""
        return '%s %s %s' % (
            sqlpuzzle._libs.sqlValue.SqlReference(self._column),
            sqlpuzzle.relations.RELATIONS[self._relation],
            sqlpuzzle._libs.sqlValue.SqlValue(self._value),
        )
    
    def __eq__(self, other):
        """Are conditions equivalent?"""
        return (
            self._column == other._column and
            self._value == other._value and
            self._relation == other._relation
        )
    
    def __ne__(self, other):
        """Are conditions not equal?"""
        return not self.__eq__(other)
    
    def __isRelationAllowed(self, relation):
        """Is relation for this value allowed?"""
        if isinstance(self._value, (str, unicode)):
            return relation in (
                sqlpuzzle.relations.EQ,
                sqlpuzzle.relations.NE,
                sqlpuzzle.relations.GT,
                sqlpuzzle.relations.GE,
                sqlpuzzle.relations.LT,
                sqlpuzzle.relations.LE,
                sqlpuzzle.relations.LIKE,
                sqlpuzzle.relations.REGEXP,
            )
        # bool is instance of int too, therefor bool must be before int
        elif isinstance(self._value, (bool,)):
            return relation in (
                sqlpuzzle.relations.EQ,
                sqlpuzzle.relations.NE,
            )
        elif isinstance(self._value, (int, long, float, datetime.date, datetime.datetime)):
            return relation in (
                sqlpuzzle.relations.EQ,
                sqlpuzzle.relations.NE,
                sqlpuzzle.relations.GT,
                sqlpuzzle.relations.GE,
                sqlpuzzle.relations.LT,
                sqlpuzzle.relations.LE,
            )
        elif isinstance(self._value, (list, tuple)):
            return relation in (
                sqlpuzzle.relations.IN,
                sqlpuzzle.relations.NOT_IN,
            )
        return False
    
    def set(self, column, value, relation=None):
        """Set column, value and relation."""
        self.setColumn(column)
        self.setValue(value)
        self.setRelation(relation or self.__defaultRelations[type(value)])
    
    def setColumn(self, column):
        """Set column."""
        self._column = column
    
    def setValue(self, value):
        """Set value."""
        self._value = value
    
    def setRelation(self, relation):
        """Set relation."""
        if not self.__isRelationAllowed(relation):
            raise sqlpuzzle.exceptions.InvalidArgumentException(
                'Relation "%s" is not allowed for data type "%s".' % (
                    sqlpuzzle.relations.RELATIONS.get(relation, 'undefined'),
                    type(self._value)
                )
            )
        
        self._relation = relation



class Conditions(sqlpuzzle._features.Features):
    def __init__(self, conditionObject=Condition):
        """Initialization of Conditions."""
        super(Conditions, self).__init__()
        self._conditionObject = conditionObject
    
    def where(self, *args, **kwds):
        """Set condition(s)."""
        if args and self.isCustumSql(args[0]):
            self._features.append(args[0])
        
        else:
            for column, value, relation in sqlpuzzle._libs.argsParser.parseArgsToListOfTuples(
                {
                    'minItems': 2,
                    'maxItems': 3,
                    'allowDict': True,
                    'allowList': True,
                    'allowedDataTypes': (
                        (str, unicode, sqlpuzzle._queries.select.Select),
                        (str, unicode, int, long, float, bool, list, tuple, datetime.date, datetime.datetime),
                        (int,)
                    ),
                },
                *args,
                **kwds
            ):
                condition = self._conditionObject()
                condition.set(column, value, relation)
                if condition not in self:
                    self._features.append(condition)
        
        return self


