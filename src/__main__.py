#!/usr/bin/python3
from user_actions import UserAction
from parse_dynamic_argument import parse_dynamic_argument
from typing import Optional, Type
import sys

action = sys.argv[1]
args = sys.argv[2:]
arguments = [
	parse_dynamic_argument(arg, action)
	for arg in args
]
FoundAction: Optional[Type[UserAction]] = None
for T in UserAction.__subclasses__():
	if action == T.command():
		FoundAction = T
		break
if FoundAction:
	FoundAction(arguments).start()
	exit_code = 0
else:
	sys.stderr.write(f"unknown sub-command: {action}\n")
	exit_code = 1
sys.exit(exit_code)
