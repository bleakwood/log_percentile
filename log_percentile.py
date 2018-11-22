import os
import sys
import subprocess
import re
import numpy as np
import pandas as pd

entries = []

# How to run: python3 log_percentile.py

# Time complexity is O(nlogn), n being lines of logs: 
# scanning through the files is of O(n) complexity, sorting is of O(nlogn) complexity, and finding the percentile is of O(1) complexity.
# So the overall time complexity is O(nlogn).
# Space complexity is O(1) given the log files are read line by line, so at any given time only one line is read from IO buffer.

if os.geteuid() == 0:
	print("Running as root!")
	for file in os.listdir('/var/log/httpd'):
		filename = os.fsdecode(file)
		if filename.endswith("log"):
			with open(os.path.join('/var/log/httpd', filename), 'r') as f:
				for line in f:
					res = re.match("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} \[\d{4}\/\d{2}\/\d{2}:\d{2}:\d{2}:\d{2}\] \"\w+ \/api\/playeritems\?playerId=\d+\" \d+ (\d+)", line)
					entries.append(int(res[1]))

	entries.sort()
	for p in (.9, .95, .99):
		idx = p * (len(entries) - 1)
		if idx % 1 == 0:
			score = entries[int(idx)]
		else:
			score = entries[int(idx)] + (entries[int(idx)+1] - entries[int(idx)]) * (idx % 1)
		print("{0:.0%} of requests return a response in {1:d} ms".format(p, int(score)))

	# series = pd.Series(np.array(entries))
	# for p in (.9, .95, .99):
	# 	print("{0:.0%} of requests return a response in {1:d} ms".format(p, int(series.quantile(p))))
else:
	print("Running this script as sudo for /var/log access.")
	subprocess.call(['sudo', 'python3', *sys.argv])