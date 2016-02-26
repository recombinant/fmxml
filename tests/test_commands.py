#!/usr/bin/env python3
# -*- mode: python tab-width: 4 coding: utf-8 -*-
import logging
import urllib.parse

import pytest

from fmxml import FMS_FIND_AND
from fmxml import \
    FMS_FIND_OP_EQ, FMS_FIND_OP_NEQ, \
    FMS_FIND_OP_GT, FMS_FIND_OP_CN, \
    FMS_FIND_OP_BW, FMS_FIND_OP_EW
from fmxml import FMS_SORT_ASCEND, FMS_SORT_DESCEND
from fmxml import FileMakerServer
from fmxml.commands.delete_command import DeleteCommand
from fmxml.commands.dup_command import DupCommand
from fmxml.commands.edit_command import EditCommand
from fmxml.commands.find_command import FindCommand
from fmxml.commands.findany_command import FindAnyCommand
from fmxml.commands.new_command import NewCommand


@pytest.fixture(scope='module')
def fms():
    fms = FileMakerServer(log_level=logging.DEBUG)
    fms.set_property('db', 'FMPHP_Sample')
    return fms


@pytest.fixture(scope='module')
def layout_name():
    return 'Form View'


def test_01_find_command(fms, layout_name):
    find_command = FindCommand(fms, layout_name)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-findall'
    assert find_command.max is None
    assert find_command.skip == 0
    assert find_command.record_id is None
    assert find_command.logical_operator is None


def test_02_find_command_max(fms, layout_name):
    find_command = FindCommand(fms, layout_name)
    assert find_command.max == None
    find_command.set_max(2)

    query = find_command.get_query()
    assert find_command.max == 2
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-max=2&' \
                    '-findall'
    find_command.set_max(None)

    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-findall'
    assert find_command.max is None


def test_03_find_command_skip(fms, layout_name):
    find_command = FindCommand(fms, layout_name)
    assert find_command.skip == 0
    find_command.set_skip(2)

    query = find_command.get_query()
    assert find_command.skip == 2
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-skip=2&' \
                    '-findall'
    find_command.set_skip(0)

    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-findall'
    assert find_command.skip == 0


def test_04_find_command_recid(fms, layout_name):
    find_command = FindCommand(fms, layout_name)
    find_command.set_record_id(7)
    assert find_command.record_id == 7

    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-recid=7&' \
                    '-find'
    find_command.set_record_id(None)

    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-findall'
    assert find_command.record_id is None


def test_05_find_command_sort_rule(fms, layout_name):
    find_command = FindCommand(fms, layout_name)
    find_command.add_sort_rule('Title', 1, FMS_SORT_ASCEND)

    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-sortfield.1=Title&' \
                    '-sortorder.1=ascend&' \
                    '-findall'

    find_command.add_sort_rule('Title', 1, FMS_SORT_DESCEND)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-sortfield.1=Title&' \
                    '-sortorder.1=descend&' \
                    '-findall'

    find_command.del_sort_rule('Title')
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-findall'

    find_command.add_sort_rule('Quantity in Stock', 1, FMS_SORT_DESCEND)
    find_command.add_sort_rule('Title', 2, FMS_SORT_ASCEND)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-sortfield.1=Quantity in Stock&' \
                    '-sortorder.1=descend&' \
                    '-sortfield.2=Title&' \
                    '-sortorder.2=ascend&' \
                    '-findall'

    find_command.del_sort_rule('Title')
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-sortfield.1=Quantity in Stock&' \
                    '-sortorder.1=descend&' \
                    '-findall'

    find_command.add_sort_rule('Title', 1, FMS_SORT_ASCEND)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-sortfield.1=Title&' \
                    '-sortorder.1=ascend&' \
                    '-findall'

    find_command.add_sort_rule('Quantity in Stock', 3, FMS_SORT_DESCEND)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-sortfield.1=Title&' \
                    '-sortorder.1=ascend&' \
                    '-sortfield.3=Quantity in Stock&' \
                    '-sortorder.3=descend&' \
                    '-findall'

    # Add a record id to make sure it reverts to -find.
    find_command.set_record_id(8)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-recid=8&' \
                    '-sortfield.1=Title&' \
                    '-sortorder.1=ascend&' \
                    '-sortfield.3=Quantity in Stock&' \
                    '-sortorder.3=descend&' \
                    '-find'

    find_command.set_record_id(None)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-sortfield.1=Title&' \
                    '-sortorder.1=ascend&' \
                    '-sortfield.3=Quantity in Stock&' \
                    '-sortorder.3=descend&' \
                    '-findall'

    find_command.clear_sort_rules()
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-findall'


def test_05_find_command_find_criteria(fms, layout_name):
    find_command = FindCommand(fms, layout_name)
    find_command.add_find_criterion('Title', 'New York 24/7', op=FMS_FIND_OP_NEQ)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    'Title=New York 24/7&' \
                    'Title.op=neq&' \
                    '-find'

    find_command = FindCommand(fms, layout_name)
    find_command.add_find_criterion('Title', 'New York 24/7', op=FMS_FIND_OP_EQ)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    'Title=New York 24/7&' \
                    'Title.op=eq&' \
                    '-find'

    find_command.clear_find_criteria()
    find_command.add_find_criterion('Title', 'as', op=FMS_FIND_OP_CN)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    'Title=as&' \
                    'Title.op=cn&' \
                    '-find'

    find_command.clear_find_criteria()
    find_command.add_find_criterion('Title', 'C', op=FMS_FIND_OP_BW)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    'Title=C&' \
                    'Title.op=bw&' \
                    '-find'

    # Add another find criterion to existing query.
    find_command.add_find_criterion('Title', 'a 24/7', op=FMS_FIND_OP_EW)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    'Title=C&' \
                    'Title.op=bw&' \
                    'Title=a 24/7&' \
                    'Title.op=ew&' \
                    '-find'

    find_command.clear_find_criteria()
    find_command.add_find_criterion('Title', 'a 24/7', op=FMS_FIND_OP_EW)
    query = find_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    'Title=a 24/7&' \
                    'Title.op=ew&' \
                    '-find'


def test_07_edit_command(fms, layout_name):
    edit_command = EditCommand(fms, layout_name, record_id=12)
    assert edit_command.mod_id is None
    edit_command.set_mod_id(2)
    assert edit_command.mod_id == 2
    edit_command.set_mod_id(3)
    assert edit_command.mod_id == 3
    edit_command.add_edit_field('Title', 'Unknown 24/7')
    query = edit_command.get_query()
    assert query == '-db=FMPHP_Sample&' \
                    '-lay=Form View&' \
                    '-recid=12&' \
                    '-modid=3&' \
                    'Title=Unknown 24/7&' \
                    '-edit'


# These queries are from the Custom Web Publishing guide.
# https://fmhelp.filemaker.com/docs/14/en/fms14_cwp_guide.pdf
#
# No command with this one:
# -db=products&-lay=sales&-field=product_image(1)&-recid=2


def test_cwp_01():
    """
    Taken from the examples in the Custom Web Publishing guide.

    https://fmhelp.filemaker.com/docs/14/en/fms14_cwp_guide.pdf
    """
    fms = FileMakerServer(log_level=logging.DEBUG)
    fms.set_property('db', 'employees')

    find_command = FindCommand(fms, 'departments')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_skip(10)
    find_command.set_max(5)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-skip=10&' \
                    '-max=5&' \
                    '-findall'

    find_command = FindCommand(fms, 'Budget')
    find_command.add_find_criterion('Salary', '100000', FMS_FIND_OP_GT)
    find_command.set_lay_response('ExecList')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=Budget&' \
                    '-lay.response=ExecList&' \
                    'Salary=100000&' \
                    'Salary.op=gt&' \
                    '-find'

    find_command = FindCommand(fms, 'departments')
    find_command.set_max(10)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-max=10&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_max('all')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-max=all&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.add_find_criterion('FirstName', 'Sam', FMS_FIND_OP_EQ)
    find_command.set_max(1)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-max=1&' \
                    'FirstName=Sam&' \
                    'FirstName.op=eq&' \
                    '-find'

    edit_command = EditCommand(fms, 'departments', record_id=13)
    edit_command.add_edit_field('Country', 'USA')
    query = edit_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-recid=13&' \
                    'Country=USA&' \
                    '-edit'

    dup_command = DupCommand(fms, 'departments', record_id=14)
    query = dup_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-recid=14&' \
                    '-dup'

    delete_command = DeleteCommand(fms, 'departments', record_id=22)
    query = delete_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-recid=22&' \
                    '-delete'

    edit_command = EditCommand(fms, 'departments', record_id=22)
    edit_command.set_mod_id(6)
    edit_command.add_edit_field('last_name', 'Jones')
    query = edit_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-recid=22&' \
                    '-modid=6&' \
                    'last_name=Jones&' \
                    '-edit'

    # Use the existing delete command.
    delete_command = DeleteCommand(fms, 'departments', record_id=4)
    query = delete_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-recid=4&' \
                    '-delete'

    find_command = FindCommand(fms, 'departments')
    find_command.set_prefind_script('myscript')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-script.prefind=myscript&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_prefind_script('myscript', 'payroll')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-script.prefind=myscript&' \
                    '-script.prefind.param=payroll&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_presort_script('myscript', '18', '65')  # convert to str first.
    find_command.add_sort_rule('dept', 1)
    find_command.add_sort_rule('rating', 2)
    query = find_command.get_query()
    assert urllib.parse.unquote_plus(
        query) == '-db=employees&' \
                  '-lay=departments&' \
                  '-script.presort=myscript&' \
                  '-script.presort.param=18|65&' \
                  '-sortfield.1=dept&' \
                  '-sortfield.2=rating&' \
                  '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_presort_script('myscript')
    find_command.add_sort_rule('dept', 1)
    find_command.add_sort_rule('rating', 2)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-script.presort=myscript&' \
                    '-sortfield.1=dept&' \
                    '-sortfield.2=rating&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_script('myscript')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-script=myscript&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_script('myscript', 'Smith', 'Chatterjee', 'Su')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-script=myscript&' \
                    '-script.param=Smith%7CChatterjee%7CSu&' \
                    '-findall'
    assert urllib.parse.unquote_plus(query) == \
           '-db=employees&' \
           '-lay=departments&' \
           '-script=myscript&' \
           '-script.param=Smith|Chatterjee|Su&' \
           '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_skip(10)
    find_command.set_max(5)

    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-skip=10&' \
                    '-max=5&' \
                    '-findall'

    # TODO: assert query == '-db=employees&-lay=departments&-view'

    edit_command = EditCommand(fms, 'departments', record_id=1)
    edit_command.add_edit_field('Country.global', 'USA')
    query = edit_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-recid=1&' \
                    'Country.global=USA&' \
                    '-edit'

    new_command = NewCommand(fms, 'departments')
    new_command.add_new_field('Country', 'Australia')
    query = new_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    'Country=Australia&' \
                    '-new'

    find_command = FindCommand(fms, 'departments')
    find_command.add_find_criterion('IDnum', '915...925')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    'IDnum=915...925&' \
                    '-find'

    find_command = FindCommand(fms, 'departments')
    find_command.set_logical_operator(FMS_FIND_AND)
    find_command.add_find_criterion('Last Name', 'Smith')
    find_command.add_find_criterion('Birthdate', '2/5/1972')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-lop=and&' \
                    'Last Name=Smith&' \
                    'Birthdate=2/5/1972&' \
                    '-find'

    find_command = FindCommand(fms, 'departments')
    find_command.add_find_criterion('name', 'Tim', FMS_FIND_OP_CN)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    'name=Tim&' \
                    'name.op=cn&' \
                    '-find'

    find_command = FindCommand(fms, 'family')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-findall'

    findany_command = FindAnyCommand(fms, 'family')
    query = findany_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-findany'

    delete_command = DeleteCommand(fms, 'family', record_id=1001)
    query = delete_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-recid=1001&' \
                    '-delete'

    edit_command = EditCommand(fms, 'family', record_id=1001)
    edit_command.set_delete_related('Dependents.3')
    query = edit_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-recid=1001&' \
                    '-delete.related=Dependents.3&' \
                    '-edit'

    edit_command = EditCommand(fms, 'family', record_id=1001)
    edit_command.add_edit_field('Dependents::Names.0', 'Timothy')
    query = edit_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-recid=1001&' \
                    'Dependents::Names.0=Timothy&' \
                    '-edit'

    edit_command = EditCommand(fms, 'family', record_id=1001)
    edit_command.add_edit_field('Dependents::Names.2', 'Kevin')
    query = edit_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-recid=1001&' \
                    'Dependents::Names.2=Kevin&' \
                    '-edit'

    edit_command = EditCommand(fms, 'family', record_id=1001)
    edit_command.add_edit_field('Dependents::Names.2', 'Kevin')
    edit_command.add_edit_field('Dependents::Names.5', 'Susan')
    query = edit_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-recid=1001&' \
                    'Dependents::Names.2=Kevin&' \
                    'Dependents::Names.5=Susan&' \
                    '-edit'

    find_command = FindCommand(fms, 'family')
    find_command.set_record_id(427)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    '-recid=427&' \
                    '-find'

    # TODO: assert query == '-db=employees&-lay=family&-view'

    find_command = FindCommand(fms, 'family')
    find_command.add_find_criterion('Country', 'USA')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    'Country=USA&' \
                    '-find'

    new_command = NewCommand(fms, 'family')
    new_command.add_new_field('FirstName', 'John')
    new_command.add_new_field('LastName', 'Doe')
    new_command.add_new_field('ID', '9756')
    new_command.add_new_field('Dependents::Names.0', 'Jane')
    query = new_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=family&' \
                    'FirstName=John&' \
                    'LastName=Doe&' \
                    'ID=9756&' \
                    'Dependents::Names.0=Jane&' \
                    '-new'

    find_command = FindCommand(fms, 'performance')
    find_command.add_sort_rule('dept', 1)
    find_command.add_sort_rule('rating', 2)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=performance&' \
                    '-sortfield.1=dept&' \
                    '-sortfield.2=rating&' \
                    '-findall'

    find_command = FindCommand(fms, 'performance')
    find_command.add_sort_rule('dept', 1, FMS_SORT_ASCEND)
    find_command.add_sort_rule('rating', 2, FMS_SORT_DESCEND)
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=performance&' \
                    '-sortfield.1=dept&' \
                    '-sortorder.1=ascend&' \
                    '-sortfield.2=rating&' \
                    '-sortorder.2=descend&' \
                    '-findall'

    find_command = FindCommand(fms, 'departments')
    find_command.set_script('myscript', 'Smith', 'Chatterjee', 'Su')
    query = find_command.get_query()
    assert query == '-db=employees&' \
                    '-lay=departments&' \
                    '-script=myscript&' \
                    '-script.param=Smith%7CChatterjee%7CSu&' \
                    '-findall'

    # TODO: assert query == '-db=employees&-layoutnames'
    # TODO: assert query == '-db=employees&-scriptnames'


def test_cwp_02():
    fms = FileMakerServer(log_level=logging.DEBUG)
    fms.set_property('db', 'career')

    edit_command = EditCommand(fms, 'applications', record_id=7)
    edit_command.set_delete_related('jobtable.20')
    query = edit_command.get_query()
    assert query == '-db=career&' \
                    '-lay=applications&' \
                    '-recid=7&' \
                    '-delete.related=jobtable.20&' \
                    '-edit'

    # TODO: assert query == '-db=FMPHP_Sample&-lay=English&-relatedsets.filter=layout&-relatedsets.max=10&-findany'
    # TODO: assert query == '-db=FMPHP_Sample&-lay=English&-relatedsets.filter=layout&-relatedsets.max=all&-findany'
    # TODO: assert query == '-db=FMPHP_Sample&-lay=English&-relatedsets.filter=none&-findany'


def test_cwp_03():
    fms = FileMakerServer(log_level=logging.DEBUG)
    fms.set_property('db', 'members')

    # A non-ASCII character.
    edit_command = EditCommand(fms, 'relationships', record_id=2)
    edit_command.add_edit_field('info', 'fiancée')
    query = edit_command.get_query()
    assert query == '-db=members&' \
                    '-lay=relationships&' \
                    '-recid=2&' \
                    'info=fianc%C3%A9e&' \
                    '-edit'
    assert urllib.parse.unquote_plus(query) == \
           '-db=members&' \
           '-lay=relationships&' \
           '-recid=2&' \
           'info=fiancée&' \
           '-edit'

    # TODO: assert query == '-db=petclinic&-lay=Patients&-query=(q1, q2);!(q3)&-q1=typeofanimal&-q1.value=Cat&-q2=color&-q2.value=Gray&-q3=name&-q3.value=Fluffy&-findquery'


def test_cwp_04():
    fms = FileMakerServer(log_level=logging.DEBUG)
    fms.set_property('db', 'products')

    find_command = FindCommand(fms, 'sales')
    query = find_command.get_query()
    assert query == '-db=products&' \
                    '-lay=sales&' \
                    '-findall'

    # TODO: assert query == '-db=vetclinic&-lay=animals &-query=(q1);(q2);!(q3)&-q1=typeofanimal&-q1.value=Cat&-q2=typeofanimal&-q2.value=Dog&-q3=name&-q3.value=Fluffy&-findquery'
    # TODO: assert query == '-dbnames'
