=====
fmxml
=====


Interface to FileMaker® Server 14 Custom Web Publishing XML


Description
===========

There are other **documented** and **working** projects in various languages
for interfacing with FileMaker® Server 14 Custom Web Publishing -
including FileMaker's own PHP.

* https://github.com/aeguana/PyFileMaker
* https://github.com/geistinteractive/fms-js
* https://github.com/mech/filemaker-ruby
* https://github.com/ginjo/rfm

This project (*fmxml*) satisfies a need and is limited in its scope.


Status
======

* Development Status :: 2 - Pre-Alpha
* Intended Audience :: Developers
* License :: OSI Approved :: BSD License
* Natural Language :: English
* Operating System :: OS Independent
* Programming Language :: Python :: 3.7 :: Only
* Topic :: Database
* Topic :: Software Development :: Libraries :: Python Modules

Examples
========

Simple example to read some data::

    params = dict()
    params['hostspec'] = 'http://localhost'
    params['username'] = 'fluffy'
    params['password'] = 'letmein'
    params['db'] = 'ACCOUNTS'

    with closing(FileMakerServer(\*\*params)) as fms:
        layout_name = 'Invoices'
        find_command = fms.create_find_records_command(layout_name)
        find_command_result = find_command.execute()

    for record in records:
        # If there were repetitions then there would be more than
        # one element in each list.
        name = record.get_field_values('Account Name')[0]
        value = record.get_field_values('Invoice Value')[0]
        date = record.get_field_values('Date')[0]

        print(f'date={date}, name={name}, value={value}')

Adding a new record::

    def add_record(fms, record_data: Dict[str, Any]):
        layout_name = 'Purchase Orders'
        new_command = fms.create_new_record_command(layout_name)
        for field_name, value in record_data.items():
            new_command.set_field_value(field_name, value)
        new_command.execute()

.. |reg|    unicode:: U+000AE .. REGISTERED SIGN