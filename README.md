flask-blog
==========

Setup
-----
`python -c "from app import db;db.create_all()"`
`python app.py`

Performance (Werkzeug development server)
-----------

	Benchmarking xxx.com (be patient)


	Server Software:        Werkzeug/0.8.1
	Server Hostname:        xxx
	Server Port:            80

	Document Path:          /
	Document Length:        1774 bytes

	Concurrency Level:      20
	Time taken for tests:   1.965 seconds
	Complete requests:      2000
	Failed requests:        0
	Write errors:           0
	Total transferred:      3858000 bytes
	HTML transferred:       3548000 bytes
	Requests per second:    1017.58 [#/sec] (mean)
	Time per request:       19.655 [ms] (mean)
	Time per request:       0.983 [ms] (mean, across all concurrent requests)
	Transfer rate:          1916.90 [Kbytes/sec] received

	Connection Times (ms)
				  min  mean[+/-sd] median   max
	Connect:        0    0   0.1      0       1
	Processing:     3   19   2.7     19      35
	Waiting:        2   19   2.7     18      35
	Total:          4   20   2.7     19      35

	Percentage of the requests served within a certain time (ms)
	  50%     19
	  66%     19
	  75%     19
	  80%     19
	  90%     21
	  95%     25
	  98%     30
	  99%     32
	 100%     35 (longest request)
	maxerize@vserver ~
	$
