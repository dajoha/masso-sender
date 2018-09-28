#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import traceback

from lib.exceptions import MassoException
import lib.cli as cli
import lib.logger as logger


def main():

    args = cli.parseCli()

    if args.send:
        if args.ip == None:
            raise MassoException("The -i option is required")
        elif args.file == '':
            raise MassoException("The -f option is required")
        else:
            import lib.masso as masso
            sender = masso.FileSender(args.ip, args.file, verbose=(not args.quiet))
            sender.start()
    else:
        import lib.gui as gui
        app = gui.MassoSenderApp(default_ip=args.ip, default_file=args.file, verbose=args.verbose)
        app.MainLoop()



if __name__ == "__main__":
    try:
        main()
    except MassoException as e:
        logger.reset()
        print(e)
    except KeyboardInterrupt:
        logger.reset()
        print "Keyboard interrupt"
    except Exception:
        logger.reset()
        traceback.print_exc()

