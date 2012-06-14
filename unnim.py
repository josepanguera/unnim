#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
from tableformatter import indent

username = ''
password = ''

def setupbr():
    # Based on code from: http://stockrt.github.com/p/emulating-a-browser-in-python-with-mechanize/

    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5')]

    return br

def login(br):
    # Open some site, let's pick a random one, the first that pops in mind:
    r = br.open('https://www.unnim.cat/SESSIONS/SFObe?ID=0&OPE=CGI_1001m_FRAME&CAN=WEB&WEB=BE')

    # Select the first (index zero) form
    br.select_form(nr=0)

    # Let's search
    br.form['1']=username
    br.form['2']=password
    br.submit()

    # Access 
    r = br.open('/appBE/SFObe?CAN=WEB&ID=0&LLAMADA=CK&Dummy=488535&OPE_REFERRER=Xmsfom.htm&OPE=PG_PosGlobal&idProces=PG_MNU&idPas=1')
    return r.read()

def posicioglobal(html):
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    accountnums = []
    for table in soup.findAll('table', {'class': 'TaulaPosGlb'}):
        print table.caption.span.text.strip().encode('utf8')
        print
        rows = []
        for tr in table.findAll('tr'):
            row = []
            for i, x in enumerate(tr.findAll(['th', 'td'])):
                text = x.text.encode('utf8').strip()
                if i != 3:
                    row.append(text)
                else:
                    # Extract account numbers
                    if re.search(r'expandeix.+LLI', text):
                        m = re.search(r'\((.+)\)', text)
                        accountnums.append(m.group(0).strip().strip('()').split(',')[0].strip().strip('\''))
            rows.append(row)
        print indent(rows, True)
        print
    return accountnums

def printlastmovements(num, html):
    print '\n\nNúmero de compte: "%s"\n' % num
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    table = soup.find('table', {'class': 'sortable'})
    rows = []
    for tr in table.findAll('tr'):
        row = []
        for x in tr.findAll(['th', 'td']):
            text = x.text.encode('utf8').strip()
            row.append(text)
        rows.append(row)
    print indent(rows, True)

def lastmovements(br, num):
    url = 'https://www.unnim.cat/appBE/SFObe?SEC=1&ID=0&CAN=WEB&IDIOMA=0&LLAMADA=CK&OPE=CM_ConsultarMoviments_SORTIDA&OPE_REFERRER=CC_ResumComptes_ENTRADA&Dummy=668397&CCC=%s&Periode=U&pasosFets=1'
    r = br.open(url % num)
    printlastmovements(num, r.read())

def main():
    if not username or not password:
		print "Error: Set username and password"
		return -1
    br = setupbr()
    resp = login(br)
    accountnums = posicioglobal(resp)
    for num in accountnums:
        lastmovements(br, num)

    return 0

if __name__ == '__main__':
    main()



