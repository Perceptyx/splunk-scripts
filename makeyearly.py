#!/usr/bin/env python
"""make yearly - collapse yearly data on top of itself for reporting multiple
years on a single overlayed chart

You can accomplish a similar thing with

    | convert timeformat="%m-%d" ctime(_time) as  day | chart sum(clients) by day,date_year

but if your data follows a monday-friday usage pattern, this chart will not look right
"""

import sys,splunk.Intersplunk
import datetime
import time

now = datetime.date.today()
day=datetime.timedelta(days=1)# so the weekday stays the same

def add_years(d, cutoff):
    added=4
    while d.year < now.year:
        d += day*364
        added+=1
        if added == 7:
            d += day*7
            added=0

    d -= 364*day
    if d.month <= cutoff:
        d += day*364
    return d

def get_results():
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions()
    cutoff = int(options.get('cutoff', 0))

    results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()

    data = []
    for r in results:
        ts = r["_time"]
        d = datetime.date.fromtimestamp(int(ts))
        tm = add_years(d, cutoff)

        if d.month > cutoff:
            r["year"] = d.year
        else:
            r["year"] = d.year-1

        r["_time"] = tm.strftime("%s")
            

    results.sort(key=lambda x: x['_time'],reverse=True)
    return results

try: 
    results = get_results()
except:
    import traceback
    stack =  traceback.format_exc()
    results = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))
splunk.Intersplunk.outputResults( results )
