#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import lib.cli as cli


if __name__ == "__main__":

    args = cli.parseCli()

    if args.send:
        if args.ip == None:
            print("The -i option is required")
        elif args.file == '':
            print("The -f option is required")
        else:
            import lib.masso as masso
            masso.sendFile(args.ip, args.file)
    else:
        import lib.gui as gui
        app = gui.MassoSenderApp(default_ip=args.ip, default_file=args.file)
        app.MainLoop()

