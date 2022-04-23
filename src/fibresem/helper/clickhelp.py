import click

class PerCommandArgWantSubCmdHelp(click.Argument):
    """https://stackoverflow.com/questions/47437472/in-python-click-how-do-i-see-help-for-subcommands-whose-parents-have-required"""
    def handle_parse_result(self, ctx, opts, args):
        """handle_parse_result"""

        # check to see if there is a --help on the command line
        if any(arg in ctx.help_option_names for arg in args):
            # if asking for help see if we are a subcommand name
            for arg in opts.values():
                if arg in ctx.command.commands:
                    # this matches a sub command name, and --help is
                    # present, let's assume the user wants help for the
                    # subcommand
                    args = [arg] + args
        return super(PerCommandArgWantSubCmdHelp, self).handle_parse_result(
            ctx, opts, args)
