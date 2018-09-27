#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cli
import gui


if __name__ == "__main__":
    args = cli.parseCli()
    app = gui.MassoSenderApp(default_ip=args.ip, default_file=args.file)
    app.MainLoop()

