from scapy.all import get_if_list
from prompt_toolkit.shortcuts import radiolist_dialog, button_dialog


result = radiolist_dialog(
    title="Interface",
    text="Select the interface to use",
    values=[
        (v, v) for v in get_if_list()
    ]
).run()

result = button_dialog(
    title='Victim IP',
    text='How do you want to enter the victim IP?',
    buttons=[
        ('Scan', True),
        ('Manual', False),
        ('Cancel', None)
    ],
).run()


print("It works!")