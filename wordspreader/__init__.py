# SPDX-FileCopyrightText: 2023-present mriswithe <1725647+mriswithe@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import logging
import os

log = logging.getLogger("wordspreader")
log.addHandler(logging.NullHandler())
if os.environ.get("WORDSPREADER_DEBUG"):
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.WARNING)
