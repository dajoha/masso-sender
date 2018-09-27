#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from lib.exceptions import MassoException
import lib.cli as cli


def main():

    args = cli.parseCli()

    if args.send:
        if args.ip == None:
            raise MassoException("The -i option is required")
        elif args.file == '':
            raise MassoException("The -f option is required")
        else:
            import lib.masso as masso
            masso.sendFile(args.ip, args.file)
    else:
        import lib.gui as gui
        app = gui.MassoSenderApp(default_ip=args.ip, default_file=args.file)
        app.MainLoop()



if __name__ == "__main__":
    try:
        main()
    except MassoException as e:
        print(e)

