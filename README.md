## README

## schedule_machine

A simple Python general purpose timing package for scheduling functions to run at defined intervals or at specifc, scheduled times.  It is specifically designed for use with Raspberry Pi.

##### Applications:

* Data acquisition, where rates are 10 hz or less
* Environment control such as for terrariums, animal habitats, etc.
* Light and appliance controls
* Surface-based drones such as slow moving wheeled and tracked vehicles, boats, model boats, etc.
* Testing machine controls
* Working with Raspberry Pi GPIO (we highly recommend using gpiozero)

##### Best Uses

Although it is possible to run schedule_machine faster, it is best for applications where you do not need faster than 10 Hz.  

Python can pose a number of challenges when running timed processes on machines.  With the appropriate warnings though, a simple timer with a well thought out control system can control machines with timing of 100 millisecond intervals and where occassionally lost functions are not disastrous.  Understanding how schedule_machine works will allow you to perform data acquisition, timing tasks, and machine control with reasonable reliability.

**WARNING - Python is not the best real-time machine control:** Python has limitations for real-time processes.  It is not true multi-threading and has a garbage collector which can be called at any time and will block all threads.  This will disrupt the process.  

**WARNING - YOUR CODE HAS TO WORK:** Timing systems are notorious hiders of bugs and glitches.  Significat testig is required to validate their reliability and, even then, they frequently are victims of oddball issues such as daylight savings time errors.  **DO NOT USE FOR SAFETY-CRITICAL or LIFE-CONTROLLING PROCESSES.**

### Quick Start

API philosophy:

1. import Timers and Chronograph classes from schedule_machine

```
from schedule_machine import Timers, Chronograph
```

2. instantiate a Timers container object

```
timers_container = Timers()
```

3. fill the timers container with timers.  Timers are defined with an interval and a function.  Note the function does not include ().  See available timers below.

```
timers_container.create_timer('every second', hello_function)
```

4. each timer calls an established function.  

```
def hello_function():
	print('Hello World')
```

5. pass the timers container to the chronograph object with time zone and run

```
Chronograph(timers_container.timer_jobs, 'US/Pacific')
```



### Attributes

* simple API with timers defined as tuples (e.g. create_timer('every second', <my_func>))
* operates on local time
* timer is run every 100 milliseconds (.1 seconds), referred to as a poll.  The poll time can be defined.
* Python queue is used to manage jobs and priorities.  By default, all jobs are run in the primary thread and are blockers.  Timer uses python_queue to put jobs into queues and execute them.
  * 'every poll' timers run sequentially and have priority.  Like all jobs, they are blockers.  If the total process time for all  'every poll' timers exceeds 100 milliseconds then it will push out the primary thread.  Eventually it will miss a poll and less than 10 polls will occur in a second.
  * Every second timers operate much like every poll but are run in queue.  Every second timers have priority over the general queue.  It is possible to overload this queue so that it eventually starts bumping jobs.
  * All other timers are run in the general queue.
* Threading:  It is possible to designate any job to run in its own thread (see below) using schedule_machine.  Remember, the jobs called by schedule_machine could already be set up as threads.  You need to watch this.  A common example are the threads created by buttons in gpiozero.



## Installation

```
pip install schedule_machine
pip3 install schedule_machine

# on Raspberry Pi using GPIO, install as root/super user:
sudo pip3 install schedule_machine
```



### Timers

Note that each timer has the format (<timer mode>, <function>).  Schedule timers have a slightly different format, defined below.

**timer mode** must be a string (e.g. 'every second') and exactly match one of the 11 timers below.

**function** must be an already created function and passed as a function object without brackets ()

```
def demo_job:
	print('this is a demo job')

# will run every 100 milliseconds (polling)
timers_container.create_timer('every poll', demo_job)

# will run every second
timers_container.create_timer('every second', demo_job)

# will run on specific times during a minute
timers_container.create_timer('on the 5 second', demo_job)
timers_container.create_timer('on the 15 second', demo_job)
timers_container.create_timer('on the 30 second', demo_job)

# will run each minute on the 00 seconds
timers_container.create_timer('every minute', demo_job)

# will run on specific minutes durin an hour
timers_container.create_timer('on the 5 minute', demo_job)
timers_container.create_timer('on the 15 minute', demo_job)
timers_container.create_timer('on the 30 minute', demo_job)

# will run each hour on the 00 minutes
timers_container.create_timer('every hour', demo_job)

# will run at a specific local time during the day.  See below.
maker.create_timer('schedule', test_function, '17:52')
```



### 'schedule' timers

'schedule' timers call a function at a specific time.  They have an additional parameter, the time they are to be called.  This time must be a string in 24 hour format 'HH:MM'.

```
#### examples of good schedule timers
maker.create_timer('schedule', test_function, '07:00')
maker.create_timer('schedule', test_function, '23:30')

#### examples of bad timer calls
maker.create_timer('schedule', test_function(), '17:52')  # function has ()
maker.create_timer('schedule', test_function, '6:52') # not in HH:MM format
maker.create_timer('schedule', test_function, '24:00')	# midnight is 00:00
```



### Time Zones

You can use any time zone included in the python pytz library (http://pytz.sourceforge.net/#what-is-utc).

Some examples of US timezones are:

```
# 'US/Aleutian', 'US/Hawaii', 'US/Alaska', 'US/Arizona', 'US/Michigan'
# 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern'
```

A note on timezone problems:  many timezones will have problems on the changeover to and from Daylight Savings time.  This is especially problematic in fall when some time zones experience the same hour twice.  One approach to deal with this is to not use the schedule timer between midnight and 1:00 AM.  Consider running daily summaries just before midnight (e.g. 23:59).

### Delay Starting the Chronograph

You may wish to instantiate the Chronograph object then either wait or pass it before starting.  You can do that as follows:

```
# create chrono object but indicate wait_to_run
chrono = Chronograph(maker.timer_jobs, 'US/Pacific', wait_to_run=True)

# start chrono directly
chrono.run_timers()
```





## Call Timer Function in a Separate Thread

Any timer can be called in its own thread using the following syntax.  A few things to be aware of when using threads:

* Python is not fully concurrent, so threads still run one at a time.
* Raspberry Pi gpiozero, which we highly encourage you to use, uses threading.  This can be problematic if you end up with competing threads.  Be careful not to have LCD or similar calls in threads where more than one thread can cause conflicting instructions to a device.

```
maker.create_timer('every minute', minute_function, None, True)  # note the None required as the third parameter.
maker.create_timer('schedule', test_function, '17:32', True)

# The format for timers is
create_timer(T_mode, func, mark, use_thread)
	T_mode: timer mode (described above)
	func: 	function the timer is calling
	mark: 	only used with T_mode 'schedule'.  Is time scheduled in 24 hour format HH:MM
	use_thread:  True or False
```



## Demo of Various Timers

This demo allows you to play around with how various timer functions interact.  It is set up initially with a long enough sleep in the 'every 15 second' function to cause the next chrono_thread to be called before the first one is complete.  The debug will show when this happens.

```
from schedule_machine.chrono import Chronograph, Timers, get_time_stamp, job_function_tester

from time import sleep

global poll_count
poll_count = 0

def poll_test():
	global poll_count
	print(poll_count, end='')
	poll_count +=1

def poll_test2():
	print('-', end='')
	sleep(.07)

def second_function():
	global poll_count
	print(get_time_stamp('US/Pacific'))
	poll_count = 0

def five_second_function():
	print('5 second function')

def fifteen_second_function():
	print('start 15 second function')
	sleep(10)
	print('end 15 second function')

def minute_function():
	print('minute function runs')

def test_function():
	print('this is the test function')

print('test run')

#### Create Timers
maker = Timers()

maker.create_timer('every poll', poll_test)
maker.create_timer('every poll', poll_test2)
maker.create_timer('every second', second_function)
maker.create_timer('on the 5 second', five_second_function)
maker.create_timer('on the 15 second', fifteen_second_function)
maker.create_timer('every minute', minute_function)

maker.create_timer('schedule', test_function, '17:32')

#### helper method to check function times
''' # explained below
job_function_tester(maker.timer_jobs)
exit()
'''

#### Run Chronograph
#Chronograph(maker.timer_jobs, 'US/Pacific')
chrono = Chronograph(maker.timer_jobs, 'US/Pacific', wait_to_run=True)

# 'US/Aleutian', 'US/Hawaii', 'US/Alaska', 'US/Arizona', 'US/Michigan'
# 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern'
chrono.run_timers(debug=True)
```



# Utilities

### Optimize Operation (job_function_tester)

A key step in optimizing a system of timers is understanding how long each called function takes.  A utility method in schedule_machine allows you to quickly get the processing time for each function.  Simply run job_function_tester(jobs) after creating timers using the Timer class.  The method is shown in context but commented out above, in the Live Demo. 

```
from schedule_machine.chrono import job_function_tester

'''
code to create timers here
'''

#### helper method to check function times
job_function_tester(maker.timer_jobs)
exit()
```



### get_time, get_time_stamp

If time information is needed in other aspects of your project you can access it using these two methods:

```
from schedule_machine.chrono import get_time, get_time_stamp

string_time_info = get_time(<time zone>)
string_time[0]	# hour as HH in 24 hour format
string_time[1]	# minute as MM
string_time[2]	# seconds as SS

time_stamp = get_time_stamp(<time zone>)  # returns time as string in HH:MM format

time_stamp = get_time_stamp(<time zone>, time_format='HMS')  # returns time as string in HH:MM:SS format
```

