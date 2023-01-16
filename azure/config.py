#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    # APP_PASSWORD = "owm8Q~YiQ6HfpSXaTsrp47gz1LI72RKiwepuHcSU"
    # APP_ID = "c5a13ca2-8ced-4d93-b423-98330ac5d987"
    ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkJZM1pKV3ViOGJIeVdpcTJIaDJVNllFR2oySSIsIng1dCI6IkJZM1pKV3ViOGJIeVdpcTJIaDJVNllFR2oySSIsInR5cCI6IkpXVCIsImN0eSI6IkpXVCJ9.eyJib3QiOiI5MDkwOTA5MDkwIiwic2l0ZSI6IkpEak4zQVVnVV9ZIiwiY29udiI6IkY4ZGkyQ1BBb2c2OEVnQnh3allTVFctdWsiLCJuYmYiOjE2NzM4NjMzMzgsImV4cCI6MTY3Mzg2NjkzOCwiaXNzIjoiaHR0cHM6Ly93ZWJjaGF0LmJvdGZyYW1ld29yay5jb20vIiwiYXVkIjoiaHR0cHM6Ly93ZWJjaGF0LmJvdGZyYW1ld29yay5jb20vIn0.dOW5Gy9yiZx_MzkCMNKja0buVRelkcmCk_yeSQvRFd8oYsdcLlLVc2jJCCbOfs6oFRruPVWAWZjlul9bUTC3-2G-JIuaA3RHoPePVAm4EedYllFnLUPQixwXkQ0CzW-9g6-KLbjQxnjw7SB_WgSQ1ZFPN8w0xDleEjiGFbwiT56by5tVQtXspLaoUYq8IxRHT1xN4j8hHQPySh2UMGXOguuJpa6EGtb9FWiE82OVDdGc1Asnl_JAZpQJVOFukhO5x-KTnPD1qHxUqLv-EOkirNYkHqOiAaxAnex4twP065g87mnYXIvtQ99sOa0qFV24EsaSbK-tLpszVvywp3BXTg"