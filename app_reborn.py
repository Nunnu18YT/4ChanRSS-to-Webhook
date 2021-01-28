import requests
from bs4 import BeautifulSoup as bs
import re
import sqlite3
import time

class RssToWebhook:
    def __init__(self, boards, webhooks):
        self.boards = boards
        self.webhooks = webhooks


# work in progress
