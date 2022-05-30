#!/usr/bin/env python3
"""
Extensive example script for using pychrome.

In order to use this script, you have to start Google Chrome/Chromium
with remote debugging as follows:
    google-chrome --remote-debugging-port=9222 --enable-automation

You can also run in headless mode, which doesn't require a graphical
user interface by supplying --headless.
"""

import pprint
import pychrome
import csv


class Crawler:

    gUrl = ""
    gAipURL = []
    gAnalyticsEnable = 0
    gAipEnable = 0


    def __init__(self, debugger_url='http://0.0.0.0:9222'):
        # Create a browser instance which controls Google Chrome/Chromium.
        self.browser = pychrome.Browser(url=debugger_url)

    def crawl_page(self, url):

        self.gAnalyticsEnable = 0
        self.gAipEnable = 0
        gUrl = url;
        # Initialize _is_loaded variable to False. It will be set to True
        # when the loadEventFired event occurs.
        self._is_loaded = False
        print("--------------------------------->>>>>>")
        # Create a tab
        self.tab = self.browser.new_tab()

        # Set callbacks for request in response logging.
        self.tab.Network.requestWillBeSent = self._event_request_will_be_sent
        self.tab.Network.responseReceived = self._event_response_received
        self.tab.Page.loadEventFired = self._event_load_event_fired

        # Start our tab after callbacks have been registered.
        self.tab.start()

        # Enable network notifications for all request/response so our
        # callbacks actually receive some data.
        self.tab.Network.enable()

        # Enable page domain notifications so our load_event_fired
        # callback is called when the page is loaded.
        self.tab.Page.enable()

        # Navigate to a specific page
        self.tab.Page.navigate(url=url, _timeout=15)

        # We wait for our load event to be fired (see `_event_load_event_fired`)
        while not self._is_loaded:
            self.tab.wait(1)

        # Wait some time for events, after the page has been loaded to look
        # for further requests from JavaScript
        self.tab.wait(10)

        # Run a JavaScript expression on the page.
        # If Google Analytics is included in the page, this expression will tell you
        # whether the site owner's wanted to enable anonymize IP. The expression will
        # fail with a JavaScript exception if Google Analytics is not in use.
        result = self.tab.Runtime.evaluate(expression="ga.getAll()[0].get('anonymizeIp')")
        #{'result': {'type': 'undefined'}}
        if result['result']['type'] == 'undefined':
            self.gAnalyticsEnable = 1
        print('------------------------>>>>>>end: ' , result)

        # Stop the tab
        self.tab.stop()

        # Close tab
        self.browser.close_tab(self.tab)


        print("analytics: " , self.gAnalyticsEnable )
        print(str(url) + ", " + str(self.gAnalyticsEnable) + ", " + str(self.gAipEnable) + "\n")
        file = open('writeToFilie.csv', "a")
        file.write(str(url) + ", " + str(self.gAnalyticsEnable) + ", " + str(self.gAipEnable) + "\n")
        file.close()
        for x in self.gAipURL:
            print(x)

    def _event_request_will_be_sent(self, request, **kwargs):
        """Will be called when a request is about to be sent.

        Those requests can still be blocked or intercepted and modified.
        This example script does not use any blocking or intercepting.

        Note: It does not say anything about the request being sucessful,
        there can still be connection issues.
        """
        if request['url'].find("aip=1") != -1:
            print("ip is anonymous in this link="+ request['url'])
            self.gAipURL.append(request['url'])
            self.gAipEnable = 1;

        pprint.pprint(request)


        #self.file.close()

    def _event_response_received(self, response, **kwargs):
        """Will be called when a response is received.

        This includes the originating request which resulted in the
        response being received.
        """
        print("fahad2\n\n")
        pprint.pprint(response)

    def _event_load_event_fired(self, timestamp, **kwargs):
        """Will be called when the page sends an load event.

        Note that this only means that all resources are loaded, the
        page may still processes some JavaScript.
        """
        self._is_loaded = True


def main():
    file = open('top_100.csv')
    csvreader = csv.reader(file)
    c = Crawler()

    #c.crawl_page('https://privacyscore.org/')
    #c.crawl_page('https://contently.com/')
    rows = []
    for row in csvreader:
        print('fahad-->  https://'+row[0].lstrip())

        c.crawl_page('https://'+row[0].lstrip())
    rows




if __name__ == '__main__':
    main()

