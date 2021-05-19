import datetime
# print with time stamp
def print_ts(*args,**kwargs):
	ts = '['+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'] '
	if 'start' in kwargs:
		print(kwargs['start'],end='')
		kwargs.pop('start')
	print(ts,end='')
	print(*args,**kwargs)

