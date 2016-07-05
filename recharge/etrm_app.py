# ===============================================================================
# Copyright 2016 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= standard library imports ========================
# ============= local library imports  ==========================


class Exit(BaseException):
    pass


HELP = {'help': 'help <command>: Display additional information about <command>',
        'exit': 'exit: Quit the application',
        'quit': 'quit: Quit the application',
        'commands': 'List all available commands'}


class App(object):
    """
    consider using curses for user interaction.
    """

    def run(self, command_line_args):
        self._welcome()

        if command_line_args:
            self._execute_commandline(command_line_args)

        while 1:
            try:
                cmd = self._get_command()
            except Exit:
                self._exit()
                break

            self._execute_command(cmd)

    def _get_command(self):
        cmd = raw_input('>>> ')
        cmd = cmd.lower()
        if cmd in ('exit', 'quit'):
            raise Exit

        return cmd

    def _execute_commandline(self, args):
        pass

    def _execute_command(self, cmd):
        cs = cmd.split(' ')
        cmd, args = cs[0], cs[1:]
        cmd = '_{}'.format(cmd)
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            func(*args)
        else:
            print 'Invalid command {}'.format(cmd)

    # commands
    def _help(self, *args):
        cmd = args[0]
        try:
            msg = HELP[cmd]
        except KeyError:
            msg = '"{}" is not a valid command'.format(cmd)
        print msg

    def _commands(self, *args):
        print '''************ Available Commands ************
commands: List all available commands
exit: Exit the program
quit: Same as exit
help <command>: Display additional information about <command>
'''

    def _welcome(self):
        print '''====================================================================================
 _______  _______  ______    __   __
|       ||       ||    _ |  |  |_|  |
|    ___||_     _||   | ||  |       |
|   |___   |   |  |   |_||_ |       |
|    ___|  |   |  |    __  ||       |
|   |___   |   |  |   |  | || ||_|| |
|_______|  |___|  |___|  |_||_|   |_|
====================================================================================
Developed by David Ketchum, Jake Ross 2016
New Mexico Tech/New Mexico Bureau of Geology


Available commands are enumerated using "commands"

For more information regarding a specific command use "help <command>". Replace <command> with the command of interest
'''

    def _exit(self):
        print 'Good Bye'


if __name__ == '__main__':
    a = App()

    args = None

    a.run(args)
# ============= EOF =============================================
