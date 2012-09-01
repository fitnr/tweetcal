#!/usr/bin/env python
# encoding: utf-8
import icalendar


def main():
    print 'hello'
    print u'#ε #δ #π #θ'.encode('utf-8')
    #print u'#ε #δ #π #θ'.decode('utf-8')
  
    e = "\u03b8".decode('utf-8')
    print e
    c = icalendar.prop.vText(e).to_ical()
    print c
    print c.encode('utf-8')

if __name__ == '__main__':
    main()
